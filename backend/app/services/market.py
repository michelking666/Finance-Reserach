"""AKShare 市场数据服务，带内存缓存（TTL 可配置）。"""
from __future__ import annotations

import time
import threading
from typing import Any

from app.services import db

_cache: dict[str, tuple[float, Any]] = {}
_lock = threading.Lock()
_TTL_SHORT = 60    # 行情/新闻：60s
_TTL_LONG = 300    # 研报/公告：5min


def _get_cache(key: str, ttl: int = _TTL_SHORT) -> Any | None:
    with _lock:
        entry = _cache.get(key)
        if entry and time.time() - entry[0] < ttl:
            return entry[1]
    return None


def _set_cache(key: str, value: Any) -> None:
    with _lock:
        _cache[key] = (time.time(), value)


def _import_ak():
    try:
        import akshare as ak
        return ak
    except ImportError:
        return None


# ── 热门股票（东财热门榜，无需全量拉取） ──────────────────
def get_hot_stocks(top_n: int = 5) -> list[dict]:
    cached = _get_cache("hot_stocks", _TTL_SHORT)
    if cached is not None:
        return cached

    ak = _import_ak()
    if ak is None:
        return []

    try:
        df = ak.stock_hot_rank_em()
        # 字段：当前排名 代码 股票名称 最新价 涨跌额 涨跌幅
        result = []
        for _, row in df.head(top_n).iterrows():
            code_raw = str(row["代码"])  # 形如 SZ002208
            suffix = code_raw[:2].lower()
            code = code_raw[2:] + ("." + suffix.upper() if suffix in ("sz", "sh") else "")
            change = float(row["涨跌幅"])
            result.append({
                "code": code,
                "name": str(row["股票名称"]),
                "price": str(row["最新价"]),
                "change": f"{change:+.2f}%",
                "up": change >= 0,
            })
        _set_cache("hot_stocks", result)
        db.save_hot_stocks(result)
        return result
    except Exception:
        return []


# ── 债券收益率（中美国债） ────────────────────────────────
def get_bond_yields() -> list[dict]:
    cached = _get_cache("bond_yields", _TTL_SHORT)
    if cached is not None:
        return cached

    ak = _import_ak()
    if ak is None:
        return []

    try:
        from datetime import date, timedelta
        start = (date.today() - timedelta(days=10)).strftime("%Y%m%d")
        df = ak.bond_zh_us_rate(start_date=start)
        if df.empty:
            return []
        row = df.iloc[-1]

        def fmt_yield(val) -> str:
            try:
                return f"{float(val):.2f}%"
            except Exception:
                return "—"

        def fmt_change(df_col, idx: int) -> str:
            try:
                if idx == 0:
                    return "—"
                cur = float(df[df_col].iloc[idx])
                prev = float(df[df_col].iloc[idx - 1])
                bp = round((cur - prev) * 100, 1)
                return f"{bp:+.1f}bp"
            except Exception:
                return "—"

        last_idx = len(df) - 1
        result = [
            {
                "code": "CN10Y",
                "name": "中国10Y国债",
                "price": fmt_yield(row.get("中国国债收益率10年")),
                "yield_": fmt_yield(row.get("中国国债收益率10年")),
                "change": fmt_change("中国国债收益率10年", last_idx),
            },
            {
                "code": "CN2Y",
                "name": "中国2Y国债",
                "price": fmt_yield(row.get("中国国债收益率2年")),
                "yield_": fmt_yield(row.get("中国国债收益率2年")),
                "change": fmt_change("中国国债收益率2年", last_idx),
            },
            {
                "code": "US10Y",
                "name": "美国10Y国债",
                "price": fmt_yield(row.get("美国国债收益率10年")),
                "yield_": fmt_yield(row.get("美国国债收益率10年")),
                "change": fmt_change("美国国债收益率10年", last_idx),
            },
        ]
        _set_cache("bond_yields", result)
        db.save_bond_yields(result)
        return result
    except Exception:
        return []


# ── 基金净值（指定代码列表） ──────────────────────────────
_WATCH_FUNDS = [
    ("110020", "易方达蓝筹精选", "主动权益"),
    ("000001", "华夏成长混合", "主动权益"),
    ("161725", "招商中证白酒", "指数"),
    ("003376", "中欧纯债债券", "纯债"),
    ("000614", "华安中短债", "中短债"),
]


def get_fund_navs() -> list[dict]:
    cached = _get_cache("fund_navs", _TTL_SHORT)
    if cached is not None:
        return cached

    ak = _import_ak()
    if ak is None:
        return []

    result = []
    for code, name, fund_type in _WATCH_FUNDS:
        try:
            df = ak.fund_open_fund_info_em(symbol=code, indicator="单位净值走势")
            if df.empty or len(df) < 2:
                continue
            last = df.iloc[-1]
            prev = df.iloc[-2]
            nav = float(last["单位净值"])
            prev_nav = float(prev["单位净值"])
            change_pct = (nav - prev_nav) / prev_nav * 100
            result.append({
                "code": code,
                "name": name,
                "nav": f"{nav:.4f}",
                "change": f"{change_pct:+.2f}%",
                "type": fund_type,
                "up": change_pct >= 0,
            })
        except Exception:
            continue

    _set_cache("fund_navs", result)
    db.save_fund_navs(result)
    return result


# ── 汇总快照 ─────────────────────────────────────────────
def get_market_snapshot() -> dict:
    return {
        "hot_stocks": get_hot_stocks(),
        "bond_yields": get_bond_yields(),
        "fund_navs": get_fund_navs(),
    }


# ── 个股卖方研报（东财） ──────────────────────────────────
def get_stock_research_reports(symbol: str, top_n: int = 5) -> list[dict]:
    """个股卖方研报列表，含机构、评级、盈利预测、PDF链接。"""
    cache_key = f"stock_reports_{symbol}"
    cached = _get_cache(cache_key, _TTL_LONG)
    if cached is not None:
        return cached

    ak = _import_ak()
    if ak is None:
        return []

    try:
        df = ak.stock_research_report_em(symbol=symbol)
        if df is None or df.empty:
            return []
        result = []
        for _, row in df.head(top_n).iterrows():
            url = str(row.get("链接", "") or "").strip()
            result.append({
                "title": str(row.get("标题", "") or "").strip(),
                "institution": str(row.get("机构", "") or "").strip(),
                "rating": str(row.get("评级", "") or "").strip(),
                "date": str(row.get("日期", "") or "").strip(),
                "url": url if url and url != "nan" else None,
                "eps_forecast": str(row.get("盈利预测", "") or "").strip(),
            })
        _set_cache(cache_key, result)
        db.save_stock_research_reports(symbol, result)
        return result
    except Exception:
        return []


# ── 个股最新新闻（东财） ──────────────────────────────────
def get_stock_news(symbol: str, top_n: int = 5) -> list[dict]:
    """个股最新新闻，含标题、摘要、来源、链接。"""
    cache_key = f"stock_news_{symbol}"
    cached = _get_cache(cache_key, _TTL_SHORT)
    if cached is not None:
        return cached

    ak = _import_ak()
    if ak is None:
        return []

    try:
        df = ak.stock_news_em(symbol=symbol)
        if df is None or df.empty:
            return []
        result = []
        for _, row in df.head(top_n).iterrows():
            url = str(row.get("新闻链接", "") or "").strip()
            content = str(row.get("新闻内容", "") or "").strip()
            result.append({
                "title": str(row.get("新闻标题", "") or "").strip(),
                "content": content[:200] if content else "",
                "date": str(row.get("发布时间", "") or "").strip(),
                "source": str(row.get("文章来源", "") or "").strip(),
                "url": url if url and url != "nan" else None,
            })
        _set_cache(cache_key, result)
        db.save_stock_news(symbol, result)
        return result
    except Exception:
        return []


# ── 基金公告/季报/年报（东财） ────────────────────────────
def get_fund_announcements(symbol: str, top_n: int = 5) -> list[dict]:
    """基金公告列表，含标题、类型、日期、链接。"""
    cache_key = f"fund_ann_{symbol}"
    cached = _get_cache(cache_key, _TTL_LONG)
    if cached is not None:
        return cached

    ak = _import_ak()
    if ak is None:
        return []

    try:
        df = ak.fund_announcement_report_em(symbol=symbol)
        if df is None or df.empty:
            return []
        result = []
        for _, row in df.head(top_n).iterrows():
            url = str(row.get("公告链接", "") or "").strip()
            result.append({
                "title": str(row.get("公告标题", "") or "").strip(),
                "type": str(row.get("公告类型", "") or "").strip(),
                "date": str(row.get("公告日期", "") or "").strip(),
                "url": url if url and url != "nan" else None,
            })
        _set_cache(cache_key, result)
        db.save_fund_announcements(symbol, result)
        return result
    except Exception:
        return []


def clear_cache() -> None:
    with _lock:
        _cache.clear()


def refresh_all() -> None:
    """清空内存缓存并重新从 AKShare 拉取全局行情数据，写入数据库。"""
    clear_cache()
    get_hot_stocks()
    get_bond_yields()
    get_fund_navs()
