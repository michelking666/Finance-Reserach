"""LLM 服务层。

有 DEEPSEEK_API_KEY 时调用真实模型；否则降级到结构化 mock。
"""
from __future__ import annotations

import re
import random
from datetime import datetime
from typing import Any
from uuid import uuid4

from app.models import ChatMessage, Skill, Source, TopicCard
from app.data import research
from app.services import deepseek


# ── 工具 ─────────────────────────────────────────────────

def _last_user(messages: list[ChatMessage]) -> str:
    for m in reversed(messages):
        if m.role == "user":
            return m.content
    return ""


def _detect_scenario(query: str) -> str:
    q = query.lower()
    if any(k in q for k in ["公司", "股票", "财报", "估值", "宁德", "特斯拉", "台积电"]):
        return "公司深度"
    if any(k in q for k in ["行业", "产业链", "景气", "渗透率"]):
        return "行业研究"
    if any(k in q for k in ["宏观", "gdp", "通胀", "汇率", "政策", "利率", "久期", "国债"]):
        return "宏观策略"
    if any(k in q for k in ["信用", "城投", "转债", "可转债", "债券", "利差", "固收", "万科"]):
        return "债券研究"
    if any(k in q for k in ["基金", "持仓", "归因", "基金经理"]):
        return "基金研究"
    if any(k in q for k in ["催化", "事件", "日历"]):
        return "事件跟踪"
    return "综合研究"


def _extract_symbol(query: str) -> str | None:
    """从查询中提取6位股票/基金代码（兼容中文上下文）。"""
    m = re.search(r'(?<!\d)(\d{6})(?!\d)', query)
    return m.group(1) if m else None


def _fetch_realtime_sources(query: str, scenario: str) -> list[Source]:
    """按场景从 AKShare 拉取实时研报/新闻/公告，转为 Source 列表。"""
    from app.services import market

    symbol = _extract_symbol(query)
    if not symbol:
        return []

    sources: list[Source] = []

    if scenario in ("公司深度", "行业研究", "事件跟踪", "综合研究"):
        for r in market.get_stock_research_reports(symbol, top_n=5):
            if not r.get("title"):
                continue
            rating = r.get("rating", "")
            eps = r.get("eps_forecast", "")
            snippet_parts = [p for p in [f"评级：{rating}" if rating else "", f"盈利预测：{eps}" if eps else ""] if p]
            sources.append(Source(
                id=f"rt-rpt-{uuid4().hex[:8]}",
                title=r["title"],
                author=r.get("institution") or None,
                publisher=r.get("institution") or None,
                published_at=r.get("date") or None,
                url=r.get("url") or None,
                snippet="  ".join(snippet_parts) or None,
                source_type="external_report",
            ))
        for n in market.get_stock_news(symbol, top_n=3):
            if not n.get("title"):
                continue
            sources.append(Source(
                id=f"rt-news-{uuid4().hex[:8]}",
                title=n["title"],
                publisher=n.get("source") or None,
                published_at=n.get("date") or None,
                url=n.get("url") or None,
                snippet=n.get("content") or None,
                source_type="web",
            ))

    elif scenario == "基金研究":
        for a in market.get_fund_announcements(symbol, top_n=5):
            if not a.get("title"):
                continue
            sources.append(Source(
                id=f"rt-fund-{uuid4().hex[:8]}",
                title=a["title"],
                published_at=a.get("date") or None,
                url=a.get("url") or None,
                snippet=f"类型：{a['type']}" if a.get("type") else None,
                source_type="external_report",
            ))

    return sources


# ── System prompt ─────────────────────────────────────────

_SYSTEM_PROMPT_BASE = """你是一位专业的公募基金投资研究助手，服务对象是基金经理和研究员。

根据用户问题，结合你的专业知识给出投研分析回答（300-500字）。如有参考资料，优先引用并用 [来源编号] 标注；没有参考资料时，直接基于你的知识作答。

回答要求：
- 语言专业、简洁，避免废话
- 直接回答问题，不要输出 JSON 或结构化卡片
- 不要以"抱歉"或"无法"开头，直接给出分析"""

_SCENARIO_FOCUS: dict[str, str] = {
    "公司深度": "本次分析重点：业务模式与竞争壁垒、财务质量（毛利率/ROE/现金流）、估值（PE/PB/DCF）、核心催化剂与风险。",
    "行业研究": "本次分析重点：景气周期位置、供需格局、价格/库存趋势、龙头竞争格局、投资主线。",
    "宏观策略": "本次分析重点：经济增长动能、通胀/利率路径、政策取向、大类资产配置建议。",
    "债券研究": "本次分析重点：利率走势与久期策略、信用利差分层、品种选择（利率债/信用债/转债）、风险提示。",
    "基金研究": "本次分析重点：持仓结构与行业暴露、超额收益来源、风险指标（最大回撤/夏普）、基金经理风格。",
    "事件跟踪": "本次分析重点：事件背景与市场影响、受益/受损标的、后续催化剂时间表。",
    "综合研究": "综合分析相关研报，提炼核心观点和投资建议。",
}


def _build_system_prompt(scenario: str) -> str:
    focus = _SCENARIO_FOCUS.get(scenario, _SCENARIO_FOCUS["综合研究"])
    return f"{_SYSTEM_PROMPT_BASE}\n\n{focus}"


def _build_messages(
    messages: list[ChatMessage],
    skill: Skill | None,
    internal_sources: list[Source],
    scenario: str,
) -> list[dict]:
    user_query = _last_user(messages)

    actual_query = (
        skill.prompt_template.replace("{input}", user_query)
        if skill else user_query
    )

    history = [
        {"role": m.role, "content": m.content}
        for m in messages[:-1]
        if m.role in ("user", "assistant")
    ]

    ctx_parts: list[str] = []
    if internal_sources:
        lines = []
        for i, s in enumerate(internal_sources):
            lines.append(
                f"[{i+1}] 《{s.title}》{f'— {s.publisher}' if s.publisher else ''}"
                f"{f' ({s.published_at})' if s.published_at else ''}\n    摘要：{s.snippet or '无'}"
            )
        ctx_parts.append("--- 内部研报参考（如相关请引用）---\n" + "\n".join(lines))

    user_content = actual_query
    if ctx_parts:
        user_content = actual_query + "\n\n" + "\n\n".join(ctx_parts)

    return [
        {"role": "system", "content": _build_system_prompt(scenario)},
        *history,
        {"role": "user", "content": user_content},
    ]


def _extract_bullets(text: str, n: int = 3) -> list[str]:
    """从回答文本中提取前 n 条要点（优先取编号行，否则取前 n 句）。"""
    bullets: list[str] = []
    for line in text.splitlines():
        line = line.strip()
        if not line:
            continue
        if re.match(r'^[\d一二三四五六七八九十]+[\.、。\)）]', line):
            clean = re.sub(r'^[\d一二三四五六七八九十]+[\.、。\)）]\s*', '', line)
            if clean:
                bullets.append(clean[:60])
        if len(bullets) >= n:
            break
    if not bullets:
        for sent in re.split(r'[。！？\n]', text):
            sent = sent.strip()
            if len(sent) > 10:
                bullets.append(sent[:60])
            if len(bullets) >= n:
                break
    return bullets or ["详见左侧回答"]


def _build_card_metrics(scenario: str, user_query: str) -> list[dict]:
    """从数据库查与对话主体相关的已有数据作为卡片指标，不发起新的网络请求。"""
    from app.services import db

    # 债券场景：优先查询中的债券名，否则取库里最新收益率
    if scenario in ("宏观策略", "债券研究"):
        bond = db.query_bond_by_name(user_query[:10])
        if bond:
            return [
                {"label": bond["name"], "value": bond.get("price", "—"), "change": bond.get("change", "—")},
            ]
        rows = db.query_latest_bond_yields()
        return [{"label": r["name"], "value": r.get("price", "—"), "change": r.get("change", "—")} for r in rows]

    # 基金场景：按名称查库
    if scenario == "基金研究":
        fund = db.query_fund_by_name(user_query[:10])
        if fund:
            return [
                {"label": fund["name"], "value": fund.get("nav", "—"), "change": fund.get("change", "—")},
            ]
        rows = db.query_latest_fund_navs()
        return [{"label": r["name"], "value": r.get("nav", "—"), "change": r.get("change", "—")} for r in rows]

    # 股票/行业/事件/综合：按名称查库
    stock = db.query_stock_by_name(user_query[:10])
    if stock:
        return [
            {"label": stock["name"], "value": stock.get("price", "—"), "change": stock.get("change", "—")},
        ]
    rows = db.query_latest_hot_stocks()
    return [{"label": r["name"], "value": r.get("price", "—"), "change": r.get("change", "—")} for r in rows]


def _build_card(
    answer_text: str,
    user_query: str,
    scenario: str,
    skill: Skill | None,
    realtime_sources: list[Source],
) -> TopicCard:
    """用 AKShare 实时数据和回答文本构建卡片，不依赖模型输出 JSON。"""
    return TopicCard(
        id=str(uuid4()),
        title=f"{scenario}：{user_query[:20]}",
        subtitle=skill.name if skill else scenario,
        summary=user_query.strip(),
        scenario=scenario,
        bullets=_extract_bullets(answer_text),
        metrics=_build_card_metrics(scenario, user_query),
        tags=[scenario, *(([skill.category] if skill else []))],
        sources=realtime_sources,
        created_at=datetime.utcnow(),
        saved=False,
    )


# ── 主入口 ────────────────────────────────────────────────

def generate_answer(
    messages: list[ChatMessage],
    skill: Skill | None = None,
    scenario_hint: str | None = None,
) -> tuple[ChatMessage, list[Source], TopicCard, list[str]]:
    """返回 (assistant 消息, 引用来源, 专题卡片, 建议技能 id 列表)。"""
    user_query = _last_user(messages)
    query = skill.prompt_template.replace("{input}", user_query) if skill else user_query
    scenario = scenario_hint or _detect_scenario(query)

    internal_sources = research.search(query, top_k=4)
    realtime_sources = _fetch_realtime_sources(query, scenario)
    all_sources = internal_sources + realtime_sources

    if deepseek.is_available():
        return _generate_with_deepseek(messages, skill, internal_sources, realtime_sources, all_sources, scenario, user_query)
    else:
        return _generate_mock(messages, skill, all_sources, scenario, user_query)


def _generate_with_deepseek(
    messages: list[ChatMessage],
    skill: Skill | None,
    internal_sources: list[Source],
    realtime_sources: list[Source],
    all_sources: list[Source],
    scenario: str,
    user_query: str,
) -> tuple[ChatMessage, list[Source], TopicCard, list[str]]:
    ds_messages = _build_messages(messages, skill, internal_sources, scenario)
    answer_text = deepseek.chat(ds_messages)

    card = _build_card(answer_text, user_query, scenario, skill, realtime_sources)
    suggested = _suggest_skills(scenario, skill_id=skill.id if skill else None)
    msg = ChatMessage(role="assistant", content=answer_text, skill_id=skill.id if skill else None)
    return msg, all_sources, card, suggested


def _generate_mock(
    messages: list[ChatMessage],
    skill: Skill | None,
    sources: list[Source],
    scenario: str,
    user_query: str,
) -> tuple[ChatMessage, list[Source], TopicCard, list[str]]:
    cite = lambda s: f"[{s.id}]"
    src_block = "\n".join(
        f"- {cite(s)} 《{s.title}》— {s.publisher or ''} ({s.published_at or ''})"
        for s in sources
    )
    answer_text = (
        f"⚠️ 当前为演示模式（未配置 DEEPSEEK_API_KEY）\n\n"
        f"基于已检索到的 {len(sources)} 篇研报/咨询资料，针对你的问题给出如下要点：\n\n"
        f"1. 核心观点：{user_query[:60]}……该主题当前处于结构性机会窗口，可关注下文卡片中的核心指标变化。{cite(sources[0]) if sources else ''}\n"
        f"2. 数据支撑：上下游价格、库存与渗透率指标在最新一期出现拐点信号。{cite(sources[1]) if len(sources) > 1 else ''}\n"
        f"3. 风险提示：需警惕海外需求波动与政策不确定性。{cite(sources[-1]) if sources else ''}\n\n"
        f"参考资料：\n{src_block}\n\n"
        f"右侧已为你生成「{scenario}」主题卡片，可一键保存到卡片中心。"
    )
    card = TopicCard(
        id=str(uuid4()),
        title=f"{scenario}速览：{user_query[:24]}",
        subtitle=skill.name if skill else "智能搜索自动生成",
        summary=user_query.strip() or "智能搜索自动生成的专题摘要",
        scenario=scenario,
        tags=[scenario, *([skill.category] if skill else []), "AI 生成"],
        bullets=[
            "结构性机会窗口逐步打开，核心指标出现拐点信号",
            "龙头公司业绩弹性 > 行业 β，关注集中度提升",
            "建议关注未来 30 天的事件催化",
        ],
        metrics=_mock_metrics(scenario),
        sources=sources,
        created_at=datetime.utcnow(),
        saved=False,
    )
    suggested = _suggest_skills(scenario, skill_id=skill.id if skill else None)
    msg = ChatMessage(role="assistant", content=answer_text, skill_id=skill.id if skill else None)
    return msg, sources, card, suggested


# ── 辅助 ─────────────────────────────────────────────────

def _mock_metrics(scenario: str) -> list[dict[str, Any]]:
    seeds = {
        "公司深度": [
            {"label": "PE (TTM)", "value": f"{random.uniform(15, 35):.1f}x", "change": f"{random.uniform(-15, 8):+.1f}%"},
            {"label": "毛利率", "value": f"{random.uniform(18, 42):.1f}%", "change": f"{random.uniform(-2, 4):+.1f}pp"},
            {"label": "营收 YoY", "value": f"{random.uniform(-5, 30):+.1f}%", "change": "vs 上季"},
        ],
        "行业研究": [
            {"label": "景气指数", "value": f"{random.uniform(45, 65):.1f}", "change": f"{random.uniform(-3, 5):+.1f}"},
            {"label": "价格环比", "value": f"{random.uniform(-8, 12):+.1f}%", "change": "MoM"},
            {"label": "库存月数", "value": f"{random.uniform(1.0, 4.5):.1f}", "change": "周期位置"},
        ],
        "宏观策略": [
            {"label": "GDP 预期", "value": f"{random.uniform(4.5, 5.5):.1f}%", "change": "2026E"},
            {"label": "CPI", "value": f"{random.uniform(0.5, 2.5):.1f}%", "change": "最新"},
            {"label": "10Y 国债", "value": f"{random.uniform(2.0, 2.8):.2f}%", "change": "周环比"},
        ],
        "债券研究": [
            {"label": "10Y 国债", "value": f"{random.uniform(2.1, 2.5):.2f}%", "change": f"{random.uniform(-8, 5):+.1f}bp"},
            {"label": "信用利差", "value": f"{random.uniform(60, 150):.0f}bp", "change": f"{random.uniform(-10, 8):+.1f}bp"},
            {"label": "DR007", "value": f"{random.uniform(1.7, 2.1):.2f}%", "change": "最新"},
        ],
        "基金研究": [
            {"label": "超额收益", "value": f"{random.uniform(-2, 8):+.1f}%", "change": "近 1 年"},
            {"label": "最大回撤", "value": f"{random.uniform(5, 20):.1f}%", "change": "近 1 年"},
            {"label": "夏普比率", "value": f"{random.uniform(0.5, 2.0):.2f}", "change": "近 1 年"},
        ],
    }
    return seeds.get(scenario, [
        {"label": "覆盖研报", "value": "12", "change": "近 90 天"},
        {"label": "事件催化", "value": "5", "change": "未来 30 天"},
        {"label": "推荐度", "value": "★★★★", "change": "AI 评分"},
    ])


def _suggest_skills(scenario: str, skill_id: str | None) -> list[str]:
    mapping = {
        "公司深度": ["earnings-recap", "thesis-debate", "catalyst-tracker"],
        "行业研究": ["industry-snapshot", "industry-compare", "catalyst-tracker"],
        "宏观策略": ["macro-brief", "rate-outlook", "thesis-debate"],
        "债券研究": ["credit-analysis", "bond-market-daily", "convertible-screen", "rate-outlook"],
        "基金研究": ["fund-holding-xray", "portfolio-attribution", "industry-snapshot"],
        "事件跟踪": ["catalyst-tracker", "earnings-recap"],
        "综合研究": ["company-deepdive", "industry-snapshot", "macro-brief"],
    }
    items = mapping.get(scenario, [])
    return [s for s in items if s != skill_id]
