"""技能广场接口。"""
from __future__ import annotations

from fastapi import APIRouter, HTTPException

from app.models import Skill
from app.services.store import store

router = APIRouter(prefix="/api/skills", tags=["skills"])


@router.get("", response_model=list[Skill])
def list_skills(q: str | None = None, category: str | None = None) -> list[Skill]:
    return store.list_skills(q=q, category=category)


@router.get("/{skill_id}", response_model=Skill)
def get_skill(skill_id: str) -> Skill:
    s = store.get_skill(skill_id)
    if not s:
        raise HTTPException(404, "技能不存在")
    return s
