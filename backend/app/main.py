"""FastAPI 入口。

启动：cd backend && /usr/local/bin/python3.11 -m uvicorn app.main:app --reload --port 8000
"""
from __future__ import annotations

import os
from contextlib import asynccontextmanager
from pathlib import Path

from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# 加载 backend/.env
load_dotenv(Path(__file__).parent.parent / ".env")

from app.routers import cards, chat, market, search, skills
from app.services import db, scheduler


@asynccontextmanager
async def lifespan(app: FastAPI):
    db.init()
    scheduler.start()
    yield
    scheduler.shutdown()


app = FastAPI(title="AI Search · 智能研究搜索", version="0.1.0", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(chat.router)
app.include_router(cards.router)
app.include_router(skills.router)
app.include_router(search.router)
app.include_router(market.router)


@app.get("/api/health")
def health() -> dict[str, str]:
    return {"status": "ok"}
