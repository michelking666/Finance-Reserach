"""市场行情路由：/api/market"""
from __future__ import annotations

import threading
from fastapi import APIRouter
from app.services import market

router = APIRouter(prefix="/api/market", tags=["market"])


def _bg(fn, *args, **kwargs):
    """在后台线程中执行 AKShare 调用，不阻塞请求线程池。"""
    threading.Thread(target=fn, args=args, kwargs=kwargs, daemon=True).start()


@router.get("/snapshot")
def market_snapshot():
    """返回缓存数据；若缓存为空则触发后台刷新，下次请求时返回结果。"""
    from app.services.market import _get_cache, get_hot_stocks, get_bond_yields, get_fund_navs
    hot = _get_cache("hot_stocks") or []
    bonds = _get_cache("bond_yields") or []
    funds = _get_cache("fund_navs") or []
    if not hot:
        _bg(get_hot_stocks)
    if not bonds:
        _bg(get_bond_yields)
    if not funds:
        _bg(get_fund_navs)
    return {"hot_stocks": hot, "bond_yields": bonds, "fund_navs": funds}


@router.get("/hot-stocks")
def hot_stocks(top_n: int = 10):
    from app.services.market import _get_cache, get_hot_stocks
    cached = _get_cache("hot_stocks") or []
    if not cached:
        _bg(get_hot_stocks, top_n=top_n)
    return cached[:top_n]


@router.get("/bond-yields")
def bond_yields():
    from app.services.market import _get_cache, get_bond_yields
    cached = _get_cache("bond_yields") or []
    if not cached:
        _bg(get_bond_yields)
    return cached


@router.get("/fund-navs")
def fund_navs():
    from app.services.market import _get_cache, get_fund_navs
    cached = _get_cache("fund_navs") or []
    if not cached:
        _bg(get_fund_navs)
    return cached
