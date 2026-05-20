"""模拟研报数据库（内部研报 / 外部研报 / 外部咨询）。

生产环境替换为向量库（如 Milvus / Qdrant）+ 全文检索。
"""
from __future__ import annotations

from app.models import Source


RESEARCH_CORPUS: list[Source] = [
    Source(
        id="r-001",
        title="新能源车产业链 2026 年中期策略",
        author="王明",
        publisher="内部研究所·新能源组",
        published_at="2026-04-22",
        snippet="2026 年新能源车渗透率有望突破 45%，碳酸锂价格触底回升，关注电池一体化与固态电池主题。",
        source_type="internal_report",
    ),
    Source(
        id="r-002",
        title="宁德时代深度：动力电池龙头格局重塑",
        author="李华",
        publisher="内部研究所·电新组",
        published_at="2026-03-15",
        snippet="公司海外装机份额提升至 28%，毛利率改善，神行电池放量为 2026 业绩提供支撑。",
        source_type="internal_report",
    ),
    Source(
        id="r-003",
        title="China Macro Outlook Q2 2026",
        author="Morgan Stanley",
        publisher="Morgan Stanley Research",
        published_at="2026-04-10",
        url="https://example.com/ms-china-macro",
        snippet="GDP growth forecast revised to 5.1% with property stabilization and consumption rebound.",
        source_type="external_report",
    ),
    Source(
        id="r-004",
        title="半导体 AI 算力链景气度跟踪",
        author="陈晨",
        publisher="内部研究所·电子组",
        published_at="2026-05-02",
        snippet="HBM 供需缺口持续，CoWoS 产能 2026H2 释放，关注先进封装与国产替代。",
        source_type="internal_report",
    ),
    Source(
        id="r-005",
        title="McKinsey: Generative AI in Financial Services 2026",
        author="McKinsey & Company",
        publisher="McKinsey",
        published_at="2026-02-28",
        url="https://example.com/mckinsey-genai-fs",
        snippet="GenAI to add $200-340B annual value to banking; investment management among top use cases.",
        source_type="external_consulting",
    ),
    Source(
        id="r-006",
        title="医药创新药出海跟踪：BD 交易显著放量",
        author="赵蕾",
        publisher="内部研究所·医药组",
        published_at="2026-04-30",
        snippet="2026Q1 国内创新药 BD 总额达 180 亿美元，ADC、双抗为热点品类。",
        source_type="internal_report",
    ),
    Source(
        id="r-007",
        title="Goldman Sachs: Global Equity Strategy May 2026",
        author="Goldman Sachs",
        publisher="Goldman Sachs Research",
        published_at="2026-05-05",
        url="https://example.com/gs-strategy",
        snippet="Overweight Asia ex-Japan; expect MSCI China EPS growth of 9% in 2026.",
        source_type="external_report",
    ),
    Source(
        id="r-008",
        title="特斯拉 FSD 与 Robotaxi 商业化时间表",
        author="孙磊",
        publisher="内部研究所·汽车组",
        published_at="2026-04-18",
        snippet="FSD v13 全量推送，Robotaxi 服务有望于 2026H2 在德州 / 加州扩展。",
        source_type="internal_report",
    ),
    # ── 债券研报 ──────────────────────────────────────────
    Source(
        id="r-009",
        title="2026 年二季度利率债策略：震荡偏多，关注久期机会",
        author="张伟",
        publisher="内部研究所·固收组",
        published_at="2026-04-25",
        snippet="资金面维持宽松，10Y 国债收益率中枢下移至 2.2%—2.4% 区间，建议适度拉长久期，关注 7—10Y 利率债配置价值。",
        source_type="internal_report",
    ),
    Source(
        id="r-010",
        title="信用债市场周报：城投利差收窄，产业债分化加剧",
        author="刘洋",
        publisher="内部研究所·固收组",
        published_at="2026-05-12",
        snippet="本周城投债利差整体收窄 3—5bp，AA+ 及以上品种受机构欠配驱动明显；地产债仍分化，央国企地产债与民企利差扩大至 180bp。",
        source_type="internal_report",
    ),
    Source(
        id="r-011",
        title="万科集团信用跟踪：流动性压力边际缓解",
        author="陈静",
        publisher="内部研究所·固收组",
        published_at="2026-05-08",
        snippet="万科 2026Q1 销售回款改善，短期债务压力有所缓解，但再融资渠道仍受限，建议持有存量债至到期，谨慎参与新发。",
        source_type="internal_report",
    ),
    Source(
        id="r-012",
        title="可转债策略月报：低溢价品种性价比凸显",
        author="王芳",
        publisher="内部研究所·固收组",
        published_at="2026-05-06",
        snippet="当前可转债平均溢价率回落至 22%，百元以下低价转债数量增至 68 只，建议关注正股基本面改善、溢价率低于 15% 的品种。",
        source_type="internal_report",
    ),
    Source(
        id="r-013",
        title="中资美元债市场跟踪：高收益板块企稳",
        author="李明远",
        publisher="内部研究所·固收组",
        published_at="2026-04-28",
        snippet="中资美元债高收益板块利差较年初收窄 60bp，地产美元债违约率趋于稳定，投资级中资美元债受美债收益率下行提振。",
        source_type="internal_report",
    ),
    Source(
        id="r-014",
        title="固定收益 2026 年中期展望：债牛延续，信用下沉需谨慎",
        author="Deutsche Bank",
        publisher="Deutsche Bank Research",
        published_at="2026-04-15",
        url="https://example.com/db-china-credit",
        snippet="China onshore bond market to remain supported by accommodative policy; credit differentiation to widen between SOE and private issuers.",
        source_type="external_report",
    ),
    # ── 基金研究 ──────────────────────────────────────────
    Source(
        id="r-015",
        title="主动权益基金 2026Q1 持仓分析：科技超配创新高",
        author="赵晓",
        publisher="内部研究所·基金研究组",
        published_at="2026-04-20",
        snippet="2026Q1 主动权益基金科技板块超配比例升至 18.5%，消费低配延续，医药持仓分化，头部基金经理换手率明显下降。",
        source_type="internal_report",
    ),
    Source(
        id="r-016",
        title="债券基金规模与业绩跟踪：纯债基金净值创新高",
        author="孙晨",
        publisher="内部研究所·基金研究组",
        published_at="2026-05-10",
        snippet="2026 年以来纯债基金平均收益率 2.8%，规模扩张至 8.2 万亿，中短债基金受零售资金青睐，久期策略分化明显。",
        source_type="internal_report",
    ),
]


_DOMAIN_KEYWORDS = [
    "新能源", "电池", "宁德", "半导体", "ai", "算力", "医药", "宏观", "策略", "特斯拉",
    "债券", "利率", "信用", "城投", "转债", "可转债", "固收", "久期", "利差", "万科",
    "基金", "持仓", "归因", "权益", "纯债", "基金经理",
]


def search(query: str, top_k: int = 4) -> list[Source]:
    """极简关键词召回。生产中替换为向量召回 + reranker。
    无匹配时返回空列表，不 fallback，避免无关研报干扰模型回答。
    """
    q = (query or "").lower()
    if not q:
        return []
    scored: list[tuple[int, Source]] = []
    for s in RESEARCH_CORPUS:
        hay = " ".join(filter(None, [s.title, s.snippet or "", s.publisher or ""])).lower()
        score = sum(1 for token in q.split() if token in hay)
        for kw in _DOMAIN_KEYWORDS:
            if kw in q and kw in hay:
                score += 2
        if score > 0:
            scored.append((score, s))
    scored.sort(key=lambda x: x[0], reverse=True)
    return [s for _, s in scored[:top_k]]
