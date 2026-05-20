"""预置技能（技能广场默认内容）。"""
from __future__ import annotations

from app.models import Skill


SKILL_SEED: list[Skill] = [
    # ── 公司分析 ──────────────────────────────────────────
    Skill(
        id="company-deepdive",
        name="公司深度画像",
        description="对单只股票做一键深度画像：业务、财务、估值、催化剂、风险。",
        category="公司分析",
        icon="🏢",
        prompt_template="请基于内外部研报，对 {input} 做一份公司深度画像，包含业务结构、最近财季亮点、估值水位、近期催化与风险点。",
        sample_input="宁德时代 300750.SZ",
    ),
    Skill(
        id="earnings-recap",
        name="财报速读",
        description="把财报压成结构化摘要：超预期项、不及预期项、指引。",
        category="公司分析",
        icon="📈",
        prompt_template="请对 {input} 最新财报做结构化摘要：营收/利润、超/不及预期项、毛利率、指引、关键问答。",
        sample_input="台积电 2026Q1",
    ),
    # ── 行业分析 ──────────────────────────────────────────
    Skill(
        id="industry-snapshot",
        name="行业景气快照",
        description="生成行业景气度卡片：上下游、价格、库存、政策、估值。",
        category="行业分析",
        icon="📊",
        prompt_template="请生成 {input} 行业的最新景气快照，覆盖上下游价格、库存周期、政策与估值水位。",
        sample_input="半导体 AI 算力",
    ),
    Skill(
        id="industry-compare",
        name="行业比较",
        description="横向对比多个行业的景气度、估值与资金流向，辅助行业配置决策。",
        category="行业分析",
        icon="🔀",
        prompt_template="请对以下行业做横向比较，覆盖景气度、PE/PB 估值分位、近期资金流向与超配/低配建议：{input}",
        sample_input="消费电子 vs 半导体 vs 新能源",
    ),
    # ── 宏观策略 ──────────────────────────────────────────
    Skill(
        id="macro-brief",
        name="宏观一页纸",
        description="把宏观主题压缩成一页纸：增长、通胀、流动性、汇率、政策。",
        category="宏观策略",
        icon="🌐",
        prompt_template="请围绕 {input} 输出一份宏观一页纸，覆盖增长、通胀、流动性、汇率与政策。",
        sample_input="2026 年中国宏观",
    ),
    Skill(
        id="rate-outlook",
        name="利率债策略",
        description="分析利率走势与久期策略：资金面、政策预期、曲线形态、配置建议。",
        category="宏观策略",
        icon="📉",
        prompt_template="请围绕 {input} 输出利率债策略分析，覆盖资金面松紧、央行政策预期、收益率曲线形态与久期/品种配置建议。",
        sample_input="2026 年二季度利率债",
    ),
    # ── 债券分析 ──────────────────────────────────────────
    Skill(
        id="credit-analysis",
        name="信用债分析",
        description="对单只或一类信用债做信用资质评估：主体评级、偿债能力、利差与风险。",
        category="债券分析",
        icon="🏦",
        prompt_template="请对 {input} 做信用债分析，覆盖发行主体资质、财务偿债能力、信用利差水位、近期舆情与投资建议。",
        sample_input="万科 2026 年到期债券",
    ),
    Skill(
        id="bond-market-daily",
        name="债市日报",
        description="生成债券市场日报：资金面、一二级市场、信用利差、可转债。",
        category="债券分析",
        icon="📋",
        prompt_template="请生成 {input} 债券市场日报，覆盖资金面（DR007/R007）、利率债一二级、信用利差变动、可转债市场动态。",
        sample_input="2026-05-19",
    ),
    Skill(
        id="convertible-screen",
        name="可转债筛选",
        description="按溢价率、正股弹性、评级等条件筛选可转债投资机会。",
        category="债券分析",
        icon="🔄",
        prompt_template="请基于以下条件筛选可转债投资机会，并给出推荐理由：{input}",
        sample_input="溢价率 < 20%，正股评级买入，剩余期限 > 1 年",
    ),
    # ── 基金研究 ──────────────────────────────────────────
    Skill(
        id="fund-holding-xray",
        name="基金持仓穿透",
        description="穿透分析基金持仓：行业集中度、重仓股变动、风格漂移、与基准偏离。",
        category="基金研究",
        icon="🔍",
        prompt_template="请对 {input} 做持仓穿透分析，覆盖行业集中度、前十大重仓股变动、风格（价值/成长/规模）漂移与相对基准的主动偏离。",
        sample_input="易方达蓝筹精选 110020",
    ),
    Skill(
        id="portfolio-attribution",
        name="组合归因",
        description="对基金或组合做 Brinson 归因：行业配置效应、个股选择效应、交互效应。",
        category="基金研究",
        icon="🧮",
        prompt_template="请对 {input} 做最近一个季度的 Brinson 业绩归因，分解行业配置效应、个股选择效应与交互效应，并指出超额收益的主要来源。",
        sample_input="某主动权益基金 vs 沪深 300",
    ),
    # ── 数据 ──────────────────────────────────────────────
    Skill(
        id="catalyst-tracker",
        name="催化剂日历",
        description="梳理未来 30 天的事件催化日历，可按行业/公司。",
        category="数据",
        icon="📅",
        prompt_template="请列出 {input} 未来 30 天的事件催化剂日历（发布会、订单、政策、财报等）。",
        sample_input="AI 算力链",
    ),
    # ── 写作 ──────────────────────────────────────────────
    Skill(
        id="thesis-debate",
        name="多空辩论",
        description="对一个投资逻辑做多空双方辩论，列举核心论据与反驳。",
        category="写作",
        icon="⚖️",
        prompt_template="对以下投资逻辑做多空辩论，列出多方与空方各 5 条核心论据并相互反驳：{input}",
        sample_input="新能源车行业 2026 年估值修复",
    ),
    Skill(
        id="research-summary",
        name="研报摘要",
        description="把一篇长研报压缩成 300 字结构化摘要：核心观点、数据支撑、风险。",
        category="写作",
        icon="✍️",
        prompt_template="请将以下研报内容压缩为 300 字结构化摘要，包含核心观点、关键数据支撑与主要风险：{input}",
        sample_input="粘贴研报正文或标题",
    ),
]
