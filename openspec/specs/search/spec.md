# Spec: 研报搜索

## 能力描述

系统提供研究报告检索能力，支持独立搜索接口和 LLM 对话中的自动引用。

## 当前实现：关键词搜索

`data/research.py` 维护一个静态语料库（`RESEARCH_CORPUS`），通过简单 token 匹配实现搜索。

### 语料库

硬编码的 `list[Source]`，包含约 15 条模拟研报：
- 内部研报（`internal_report`）：内部研究所各组出品
- 外部研报（`external_report`）：Morgan Stanley、Goldman Sachs 等
- 外部咨询（`external_consulting`）：McKinsey 等

### 搜索逻辑

```python
def search(query: str, top_k: int = 8) -> list[Source]:
    # 将 query 分词（空格/中文字符切分）
    # 对每条 Source 的 title + snippet + author + publisher 做 token 匹配
    # 按匹配 token 数量降序排列，返回 top_k 条
    # query 为空时返回全部语料
```

### 已知问题

- **语义匹配差**：关键词不命中时返回空，无法理解同义词或上下文
- **语料静态**：无法动态添加真实研报
- **无相关性排序**：仅按 token 命中数量排序，无向量相似度

## 目标实现：Qdrant 向量搜索

见 change: `vector-search`。

## API 接口

```
GET /api/search?q=<query>&top_k=<n>
→ list[Source]
```

## LLM 集成

`llm.generate_answer` 调用 `research.search(query, top_k=4)` 获取内部研报，作为 LLM 上下文的一部分传入 DeepSeek。

## 数据模型

```
Source
  id: str
  title: str
  author: str | None
  publisher: str | None
  published_at: str | None
  url: str | None
  snippet: str | None
  source_type: internal_report | external_report | external_consulting | web
```

## 集成点

- `backend/app/data/research.py` — 语料库与搜索逻辑
- `backend/app/routers/search.py` — HTTP 接口
- `backend/app/services/llm.py` — 对话中自动引用
