# Proposal: 流式输出

## 问题

当前 `/api/chat` 是同步接口，DeepSeek 完整生成后才返回，用户等待时无任何反馈，体验差（尤其是长回答）。

## 目标

将聊天接口改为 SSE（Server-Sent Events）流式输出，前端实时渲染打字机效果。

## 方案

新增 `POST /api/chat/stream` 接口，使用 FastAPI `StreamingResponse` + `deepseek.chat_stream`（已实现）逐块推送文本。卡片和来源在流结束后通过最后一个 SSE event 推送。前端用 `EventSource` 或 `fetch` + `ReadableStream` 接收。

## Non-goals

- 不废弃原有 `/api/chat` 同步接口（保留作为降级）
- 不做 WebSocket（SSE 单向推送已满足需求）
- 不做流式卡片生成（卡片在流结束后一次性返回）

## 影响范围

- `backend/app/routers/chat.py` — 新增 POST /api/chat/stream
- `backend/app/services/llm.py` — 新增 `generate_answer_stream` 生成器函数
- `frontend/src/api/client.ts` — 新增 `chatStream` 方法
- `frontend/src/pages/SearchPage.tsx` — 改为流式渲染

## 前置条件

- user-auth change 已完成（流式接口同样需要鉴权）

## 优先级

低。同步接口功能完整，流式输出是体验优化，在 persistent-storage 和 user-auth 完成后再做。
