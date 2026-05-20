"""技能广场接口。"""
from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException

from app.models import Skill
from app.services.auth import get_current_user
from app.services.store import store

router = APIRouter(prefix="/api/skills", tags=["skills"])


@router.get("", response_model=list[Skill])
def list_skills(q: str | None = None, category: str | None = None, _: dict = Depends(get_current_user)) -> list[Skill]:
    return store.list_skills(q=q, category=category)


@router.get("/{skill_id}", response_model=Skill)
def get_skill(skill_id: str, _: dict = Depends(get_current_user)) -> Skill:
    s = store.get_skill(skill_id)
    if not s:
        raise HTTPException(404, "技能不存在")
    return s
