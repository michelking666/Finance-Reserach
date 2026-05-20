# Proposal: 向量搜索

## 问题

`data/research.py` 使用关键词 token 匹配，语义理解差，同义词不命中，无法支持真实研报入库和语义检索。

## 目标

用 Qdrant 替换关键词搜索，支持语义向量检索，并提供研报入库接口，使搜索质量从"关键词命中"升级到"语义相关"。

## 方案

本地部署 Qdrant（Docker），使用 DeepSeek embedding 或 sentence-transformers 生成向量。`research.search` 改为查询 Qdrant collection，保持函数签名不变。新增管理接口用于研报入库。

## Non-goals

- 不做全文检索（纯向量搜索，不做混合检索）
- 不做研报 PDF 解析（只处理文本字段）
- 不做向量模型微调
- 不迁移 AKShare 实时数据到 Qdrant（实时数据继续走 PostgreSQL）

## 影响范围

- `backend/app/data/research.py` — 改为 Qdrant 查询，保持 `search(query, top_k)` 签名
- `backend/app/services/qdrant.py` — 新增（Qdrant 客户端封装，向量化，upsert，search）
- `backend/app/routers/search.py` — 新增 POST /api/search/ingest（研报入库）
- `backend/requirements.txt` — 新增 `qdrant-client`、`sentence-transformers` 或调用 embedding API
- `backend/.env.example` — 新增 `QDRANT_URL`、`EMBEDDING_MODEL`
- `docker-compose.yml` — 新增（Qdrant 本地服务）

## 前置条件

- persistent-storage change 已完成（数据库基础设施就绪）
