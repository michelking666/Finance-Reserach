"""Pydantic 模型定义：聊天消息、来源、卡片、技能等。"""
from __future__ import annotations

from datetime import datetime
from typing import Any, Literal, Optional
from uuid import uuid4

from pydantic import BaseModel, Field


# ---------- 数据来源 ----------
class Source(BaseModel):
    id: str
    title: str
    author: Optional[str] = None
    publisher: Optional[str] = None
    published_at: Optional[str] = None
    url: Optional[str] = None
    snippet: Optional[str] = None
    source_type: Literal["internal_report", "external_report", "external_consulting", "web"] = "internal_report"


# ---------- 聊天 ----------
class ChatMessage(BaseModel):
    role: Literal["user", "assistant", "system"]
    content: str
    skill_id: Optional[str] = None  # 用户调用某个技能时传入


class ChatRequest(BaseModel):
    messages: list[ChatMessage]
    skill_id: Optional[str] = None
    scenario: Optional[str] = None  # e.g. 行业研究/公司深度/宏观策略


class TopicCard(BaseModel):
    """聊天回答中动态生成的专题卡片。"""
    id: str = Field(default_factory=lambda: str(uuid4()))
    title: str
    subtitle: Optional[str] = None
    summary: str
    tags: list[str] = []
    metrics: list[dict[str, Any]] = []  # [{label, value, change}]
    bullets: list[str] = []
    scenario: Optional[str] = None
    sources: list[Source] = []
    created_at: datetime = Field(default_factory=datetime.utcnow)
    saved: bool = False


class ChatResponse(BaseModel):
    message: ChatMessage
    sources: list[Source] = []
    card: Optional[TopicCard] = None
    suggested_skills: list[str] = []


# ---------- 卡片中心 ----------
class CardCreateRequest(BaseModel):
    title: str
    subtitle: Optional[str] = None
    summary: str
    tags: list[str] = []
    metrics: list[dict[str, Any]] = []
    bullets: list[str] = []
    scenario: Optional[str] = None
    sources: list[Source] = []


# ---------- 技能 ----------
class Skill(BaseModel):
    id: str
    name: str
    description: str
    category: str  # e.g. 公司分析/行业分析/宏观/数据/写作
    icon: str = "✨"
    prompt_template: str  # 含 {input} 占位符
    sample_input: Optional[str] = None
    output_kind: Literal["text", "card", "table"] = "card"
