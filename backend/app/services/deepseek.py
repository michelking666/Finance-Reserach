"""DeepSeek API 客户端封装。

使用 openai 兼容 SDK，base_url 指向 DeepSeek。
支持普通调用和流式（SSE）调用。
"""
from __future__ import annotations

import os
from typing import Iterator

from openai import OpenAI
from openai.types.chat import ChatCompletionMessageParam

DEFAULT_MODEL = "deepseek-v4-flash"
DEFAULT_BASE_URL = "https://api.deepseek.com"

# 不缓存 client，每次从环境变量读取，避免 .env 加载时序问题
def _get_client() -> OpenAI:
    api_key = os.getenv("DEEPSEEK_API_KEY", "").strip()
    if not api_key:
        raise RuntimeError("DEEPSEEK_API_KEY 未配置")
    base_url = os.getenv("DEEPSEEK_BASE_URL", DEFAULT_BASE_URL).rstrip("/")
    return OpenAI(
        api_key=api_key,
        base_url=base_url,
        timeout=None,
    )


def is_available() -> bool:
    return bool(os.getenv("DEEPSEEK_API_KEY", "").strip())


def chat(
    messages: list[ChatCompletionMessageParam],
    model: str | None = None,
) -> str:
    """普通调用，返回完整回答文本。"""
    client = _get_client()
    model = model or os.getenv("DEEPSEEK_MODEL", DEFAULT_MODEL)
    resp = client.chat.completions.create(
        model=model,
        messages=messages,
        stream=False,
        reasoning_effort="high",
        extra_body={"thinking": {"type": "enabled"}},
    )
    return resp.choices[0].message.content or ""


def chat_stream(
    messages: list[ChatCompletionMessageParam],
    model: str | None = None,
) -> Iterator[str]:
    """流式调用，逐块 yield 文本片段。"""
    client = _get_client()
    model = model or os.getenv("DEEPSEEK_MODEL", DEFAULT_MODEL)
    stream = client.chat.completions.create(
        model=model,
        messages=messages,
        stream=True,
        reasoning_effort="high",
        extra_body={"thinking": {"type": "enabled"}},
    )
    for chunk in stream:
        delta = chunk.choices[0].delta.content
        if delta:
            yield delta

