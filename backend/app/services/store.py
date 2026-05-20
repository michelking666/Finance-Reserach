"""存储层：卡片优先走 PostgreSQL，DB 不可用时降级内存。技能始终内存。"""
from __future__ import annotations

from threading import RLock
from typing import Iterable
from uuid import uuid4

from app.data.skills_seed import SKILL_SEED
from app.models import Skill, TopicCard
from app.services import db


class _Store:
    def __init__(self) -> None:
        self._lock = RLock()
        self._mem_cards: dict[str, TopicCard] = {}
        self._skills: dict[str, Skill] = {s.id: s for s in SKILL_SEED}

    # ---------- 卡片 ----------
    def list_cards(self, only_saved: bool = False) -> list[TopicCard]:
        rows = db.list_cards(only_saved=only_saved)
        if rows:
            return [TopicCard.model_validate(r) for r in rows]
        # 降级：内存
        with self._lock:
            items = list(self._mem_cards.values())
        if only_saved:
            items = [c for c in items if c.saved]
        items.sort(key=lambda c: c.created_at, reverse=True)
        return items

    def get_card(self, card_id: str) -> TopicCard | None:
        row = db.get_card(card_id)
        if row is not None:
            return TopicCard.model_validate(row)
        with self._lock:
            return self._mem_cards.get(card_id)

    def upsert_card(self, card: TopicCard) -> TopicCard:
        if not card.id:
            card.id = str(uuid4())
        db.upsert_card(card.model_dump(mode="json"))
        # 同步内存（降级备份）
        with self._lock:
            self._mem_cards[card.id] = card
        return card

    def delete_card(self, card_id: str) -> bool:
        ok = db.delete_card(card_id)
        with self._lock:
            mem_ok = self._mem_cards.pop(card_id, None) is not None
        return ok or mem_ok

    def toggle_save(self, card_id: str, saved: bool) -> TopicCard | None:
        row = db.toggle_save(card_id, saved)
        if row is not None:
            card = TopicCard.model_validate(row)
            with self._lock:
                self._mem_cards[card_id] = card
            return card
        # 降级：内存
        with self._lock:
            card = self._mem_cards.get(card_id)
            if not card:
                return None
            card.saved = saved
            return card

    # ---------- 技能 ----------
    def list_skills(self, q: str | None = None, category: str | None = None) -> list[Skill]:
        with self._lock:
            items: Iterable[Skill] = self._skills.values()
        if category:
            items = [s for s in items if s.category == category]
        if q:
            ql = q.lower()
            items = [s for s in items if ql in s.name.lower() or ql in s.description.lower()]
        return list(items)

    def get_skill(self, skill_id: str) -> Skill | None:
        with self._lock:
            return self._skills.get(skill_id)


store = _Store()
