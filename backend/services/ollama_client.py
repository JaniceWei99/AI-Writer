"""
Legacy Ollama client — kept for backward compatibility.

The primary LLM entry point is now ``llm_provider.py`` which supports
multiple providers (Ollama, OpenAI, DeepSeek, Qwen, …) and uses the
Ollama **Chat API** (``/api/chat``) with system/user message splitting.

Functions here are still used by the poetry-retry path in
``routers/writing.py`` (non-streaming generate with validation).
"""

import os
import json
from typing import AsyncGenerator, Optional

import httpx

OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
DEFAULT_MODEL = os.getenv("OLLAMA_MODEL", "qwen3.5:9b")
OLLAMA_NUM_GPU = int(os.getenv("OLLAMA_NUM_GPU", "99"))  # max layers on GPU
OLLAMA_NUM_PREDICT = int(os.getenv("OLLAMA_NUM_PREDICT", "4096"))  # max tokens


async def list_models() -> list[dict]:
    """查询 Ollama 已安装的模型列表。"""
    async with httpx.AsyncClient(timeout=10.0) as client:
        resp = await client.get(f"{OLLAMA_BASE_URL}/api/tags")
        resp.raise_for_status()
        data = resp.json()
        return data.get("models", [])


async def generate(prompt: str, model: str = DEFAULT_MODEL, temperature: Optional[float] = None) -> dict:
    """非流式调用 Ollama Chat API，返回完整结果。"""
    options: dict = {"num_gpu": OLLAMA_NUM_GPU, "num_predict": OLLAMA_NUM_PREDICT}
    if temperature is not None:
        options["temperature"] = temperature
    payload: dict = {
        "model": model,
        "messages": [{"role": "user", "content": prompt}],
        "stream": False,
        "think": False,
        "options": options,
    }
    async with httpx.AsyncClient(timeout=300.0) as client:
        resp = await client.post(f"{OLLAMA_BASE_URL}/api/chat", json=payload)
        resp.raise_for_status()
        data = resp.json()
        return {
            "text": data.get("message", {}).get("content", ""),
            "token_count": data.get("eval_count", 0),
        }


async def generate_stream(prompt: str, model: str = DEFAULT_MODEL, temperature: Optional[float] = None) -> AsyncGenerator[str, None]:
    """流式调用 Ollama Chat API，逐步返回文本。"""
    options: dict = {"num_gpu": OLLAMA_NUM_GPU, "num_predict": OLLAMA_NUM_PREDICT}
    if temperature is not None:
        options["temperature"] = temperature
    payload: dict = {
        "model": model,
        "messages": [{"role": "user", "content": prompt}],
        "stream": True,
        "think": False,
        "options": options,
    }
    async with httpx.AsyncClient(timeout=300.0) as client:
        async with client.stream(
            "POST",
            f"{OLLAMA_BASE_URL}/api/chat",
            json=payload,
        ) as resp:
            resp.raise_for_status()
            async for line in resp.aiter_lines():
                if line.strip():
                    chunk = json.loads(line)
                    token = chunk.get("message", {}).get("content", "")
                    if token:
                        yield token
                    if chunk.get("done", False):
                        break
