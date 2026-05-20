"""内存存储。生产环境替换为 PostgreSQL / Redis。"""
from __future__ import annotations

from threading import RLock
from typing import Iterable
from uuid import uuid4

from app.data.skills_seed import SKILL_SEED
from app.models import Skill, TopicCard


class _Store:
    def __init__(self) -> None:
        self._lock = RLock()
        self._cards: dict[str, TopicCard] = {}
        self._skills: dict[str, Skill] = {s.id: s for s in SKILL_SEED}

    # ---------- 卡片 ----------
    def list_cards(self, only_saved: bool = False) -> list[TopicCard]:
        with self._lock:
            items = list(self._cards.values())
        if only_saved:
            items = [c for c in items if c.saved]
        items.sort(key=lambda c: c.created_at, reverse=True)
        return items

    def get_card(self, card_id: str) -> TopicCard | None:
        with self._lock:
            return self._cards.get(card_id)

    def upsert_card(self, card: TopicCard) -> TopicCard:
        with self._lock:
            if not card.id:
                card.id = str(uuid4())
            self._cards[card.id] = card
            return card

    def delete_card(self, card_id: str) -> bool:
        with self._lock:
            return self._cards.pop(card_id, None) is not None

    def toggle_save(self, card_id: str, saved: bool) -> TopicCard | None:
        with self._lock:
            card = self._cards.get(card_id)
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
