"""聊天相关接口。"""
from __future__ import annotations

from fastapi import APIRouter, HTTPException

from app.models import ChatRequest, ChatResponse
from app.services import llm
from app.services.store import store

router = APIRouter(prefix="/api/chat", tags=["chat"])


@router.post("", response_model=ChatResponse)
def chat(req: ChatRequest) -> ChatResponse:
    if not req.messages:
        raise HTTPException(status_code=400, detail="messages 不能为空")

    skill = store.get_skill(req.skill_id) if req.skill_id else None
    if req.skill_id and not skill:
        raise HTTPException(status_code=404, detail=f"技能 {req.skill_id} 不存在")

    msg, sources, card, suggested = llm.generate_answer(
        req.messages, skill=skill, scenario_hint=req.scenario
    )
    # 自动写入卡片（未保存状态），方便前端拿到 id
    card = store.upsert_card(card)
    return ChatResponse(message=msg, sources=sources, card=card, suggested_skills=suggested)
