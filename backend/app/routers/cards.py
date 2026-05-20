"""卡片中心 CRUD。"""
from __future__ import annotations

from fastapi import APIRouter, HTTPException

from app.models import CardCreateRequest, TopicCard
from app.services.store import store

router = APIRouter(prefix="/api/cards", tags=["cards"])


@router.get("", response_model=list[TopicCard])
def list_cards(only_saved: bool = False) -> list[TopicCard]:
    return store.list_cards(only_saved=only_saved)


@router.get("/{card_id}", response_model=TopicCard)
def get_card(card_id: str) -> TopicCard:
    card = store.get_card(card_id)
    if not card:
        raise HTTPException(404, "卡片不存在")
    return card


@router.post("", response_model=TopicCard)
def create_card(req: CardCreateRequest) -> TopicCard:
    card = TopicCard(**req.model_dump(), saved=True)
    return store.upsert_card(card)


@router.patch("/{card_id}/save", response_model=TopicCard)
def save_card(card_id: str, saved: bool = True) -> TopicCard:
    card = store.toggle_save(card_id, saved)
    if not card:
        raise HTTPException(404, "卡片不存在")
    return card


@router.delete("/{card_id}")
def delete_card(card_id: str) -> dict[str, bool]:
    ok = store.delete_card(card_id)
    if not ok:
        raise HTTPException(404, "卡片不存在")
    return {"ok": True}
