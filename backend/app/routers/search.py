"""研报检索接口（独立提供，可用于卡片详情展示来源等）。"""
from __future__ import annotations

from fastapi import APIRouter

from app.data import research
from app.models import Source

router = APIRouter(prefix="/api/search", tags=["search"])


@router.get("", response_model=list[Source])
def search(q: str = "", top_k: int = 8) -> list[Source]:
    return research.search(q, top_k=top_k)
