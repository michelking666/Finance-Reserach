# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Commands

```bash
# Install dependencies (requires Python 3.11)
cd backend && /usr/local/bin/python3.11 -m pip install -r requirements.txt

# Run the dev server (must use Python 3.11 for akshare)
cd backend && /usr/local/bin/python3.11 -m uvicorn app.main:app --reload --port 8000

# Health check
curl http://localhost:8000/api/health

# Market data snapshot
curl http://localhost:8000/api/market/snapshot
```

No test runner or linter is configured yet.

## Architecture

This is a Python/FastAPI backend for an AI-powered research search tool (智能研究搜索). There is no frontend in this repo.

```
backend/
  app/
    main.py          # FastAPI app, CORS, router registration
    models.py        # All Pydantic models (Source, ChatMessage, TopicCard, Skill, etc.)
    routers/         # One file per resource: chat, cards, skills, search
    services/
      llm.py         # LLM abstraction — currently a structured mock, no real API key needed
      store.py       # In-memory store (thread-safe, RLock) — no database
      market.py      # AKShare market data service with 60s in-memory cache
    data/
      research.py    # Static corpus of mock research reports + keyword search
      skills_seed.py # Default skills loaded into the store at startup
```

### Key design points

**LLM layer is a mock.** `services/llm.py:generate_answer` returns structured fake data. To wire a real model, replace that function — the signature `(messages, skill, scenario_hint) -> (ChatMessage, list[Source], TopicCard, list[str])` is the integration point.

**Storage is in-memory.** `services/store.py` holds cards and skills in dicts behind an `RLock`. Data is lost on restart. The comments say to replace with PostgreSQL/Redis for production.

**Search is keyword-based.** `data/research.py:search` does simple token matching against a hardcoded corpus. Production replacement is a vector store (Milvus/Qdrant) + reranker.

**Chat flow:** `POST /api/chat` → resolves optional skill → calls `llm.generate_answer` → auto-saves the returned `TopicCard` to the store (unsaved state) → returns message + sources + card + suggested skill IDs.

**Scenarios** are auto-detected from query keywords in `llm._detect_scenario`: 公司深度 / 行业研究 / 宏观策略 / 事件跟踪 / 综合研究. They drive card metrics and skill suggestions.

### API surface

| Method | Path | Purpose |
|--------|------|---------|
| POST | `/api/chat` | Main chat endpoint |
| GET | `/api/search?q=&top_k=` | Standalone research search |
| GET/POST | `/api/cards` | List / create topic cards |
| GET/PATCH/DELETE | `/api/cards/{id}` | Get / save-toggle / delete card |
| GET | `/api/skills?q=&category=` | List skills |
| GET | `/api/skills/{id}` | Get skill by ID |
| GET | `/api/market/snapshot` | Hot stocks + bond yields + fund NAVs (AKShare, 60s cache) |
| GET | `/api/market/hot-stocks` | Top N hot stocks from 东财 |
| GET | `/api/market/bond-yields` | CN/US treasury yields |
| GET | `/api/market/fund-navs` | Watched fund NAVs |
