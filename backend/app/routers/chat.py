"""聊天相关接口。"""
from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException

from app.models import ChatRequest, ChatResponse
from app.services import llm
from app.services.auth import get_current_user
from app.services.store import store

router = APIRouter(prefix="/api/chat", tags=["chat"])


@router.post("", response_model=ChatResponse)
def chat(req: ChatRequest, _: dict = Depends(get_current_user)) -> ChatResponse:
    if not req.messages:
        raise HTTPException(status_code=400, detail="messages 不能为空")

    skill = store.get_skill(req.skill_id) if req.skill_id else None
    if req.skill_id and not skill:
        raise HTTPException(status_code=404, detail=f"技能 {req.skill_id} 不存在")

    msg, sources, card, suggested = llm.generate_answer(
        req.messages, skill=skill, scenario_hint=req.scenario
    )
    card = store.upsert_card(card)
    return ChatResponse(message=msg, sources=sources, card=card, suggested_skills=suggested)
