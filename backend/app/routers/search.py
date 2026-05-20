"""研报检索接口（独立提供，可用于卡片详情展示来源等）。"""
from __future__ import annotations

from fastapi import APIRouter, Depends

from app.data import research
from app.models import Source
from app.services.auth import get_current_user

router = APIRouter(prefix="/api/search", tags=["search"])


@router.get("", response_model=list[Source])
def search(q: str = "", top_k: int = 8, _: dict = Depends(get_current_user)) -> list[Source]:
    return research.search(q, top_k=top_k)
