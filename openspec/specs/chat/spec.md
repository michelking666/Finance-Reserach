# Spec: 聊天与 LLM 集成

## 能力描述

系统提供基于 LLM 的金融研究问答能力。用户发送消息，系统返回结构化回答、引用来源和专题卡片。

## 核心行为

### 请求处理流程

```
POST /api/chat
  → 解析 skill_id（可选）
  → 调用 llm.generate_answer(messages, skill, scenario_hint)
    → 检测场景（_detect_scenario）
    → 检索内部研报（research.search，top_k=4）
    → 拉取实时来源（_fetch_realtime_sources，按场景从 AKShare 获取）
    → 调用 DeepSeek 或降级 mock
    → 构建 TopicCard（_build_card）
  → 自动 upsert 卡片到 store（saved=False）
  → 返回 ChatResponse
```

### 场景检测

从用户查询关键词自动推断，共 7 种场景：

| 场景 | 触发关键词示例 |
|------|--------------|
| 公司深度 | 公司、股票、财报、估值、宁德、特斯拉 |
| 行业研究 | 行业、产业链、景气、渗透率 |
| 宏观策略 | 宏观、GDP、通胀、汇率、政策、利率 |
| 债券研究 | 信用、城投、转债、债券、利差、固收 |
| 基金研究 | 基金、持仓、归因、基金经理 |
| 事件跟踪 | 催化、事件、日历 |
| 综合研究 | （默认） |

### LLM 降级策略

- 有 `DEEPSEEK_API_KEY` → 调用真实 DeepSeek API（`deepseek.chat`）
- 无 key → 返回结构化 mock 回答，明确标注"演示模式"

### 专题卡片生成

每次对话自动生成一张 `TopicCard`，包含：
- `title`：场景 + 查询前 20 字
- `bullets`：从回答文本提取的要点（最多 5 条）
- `metrics`：从 PostgreSQL 查询相关行情数据（不发起新网络请求）
- `sources`：实时来源（AKShare 研报/新闻/公告）
- `saved=False`：默认未收藏，用户手动保存

### 技能（Skill）集成

- 技能是可选的提示词模板，含 `{input}` 占位符
- 传入 `skill_id` 时，用模板替换原始查询再送入 LLM
- 返回 `suggested_skills`：基于场景推荐 2-3 个相关技能 ID

## 数据模型

```
ChatRequest
  messages: list[ChatMessage]
  skill_id: str | None
  scenario: str | None       # 可强制指定场景

ChatResponse
  message: ChatMessage       # role=assistant
  sources: list[Source]      # 内部研报 + 实时来源
  card: TopicCard
  suggested_skills: list[str]

ChatMessage
  role: user | assistant | system
  content: str
  skill_id: str | None
```

## 集成点

- `backend/app/routers/chat.py` — 路由入口
- `backend/app/services/llm.py` — 核心逻辑
- `backend/app/services/deepseek.py` — DeepSeek 客户端
- `backend/app/services/store.py` — 卡片自动写入
- `backend/app/data/research.py` — 内部研报检索

## 当前限制

- 无对话历史持久化，每次请求独立
- 无流式输出（`deepseek.chat_stream` 已实现，前端未接入）
- 场景检测基于关键词，无语义理解
- 卡片 metrics 依赖 PostgreSQL 有数据，冷启动时为空
