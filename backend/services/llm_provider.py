"""
LLM Provider abstraction layer.

Supports:
- ollama  (default, local)
- openai  (OpenAI API)
- deepseek (DeepSeek, OpenAI-compatible)
- qwen    (通义千问/DashScope, OpenAI-compatible)

Configuration via environment variables:
  LLM_PROVIDER=ollama          (default)
  OPENAI_API_KEY=...           OPENAI_BASE_URL=...         OPENAI_MODEL=gpt-4o
  DEEPSEEK_API_KEY=...         DEEPSEEK_BASE_URL=...       DEEPSEEK_MODEL=deepseek-chat
  QWEN_API_KEY=...             QWEN_BASE_URL=...           QWEN_MODEL=qwen-plus
"""
import os
import json
import logging
from typing import AsyncGenerator, Optional

import httpx

logger = logging.getLogger("app.llm")

# ---------- Provider registry ----------

LLM_PROVIDER = os.getenv("LLM_PROVIDER", "ollama").lower()

# Ollama settings (reuse existing)
OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "qwen3.5:9b")

# OpenAI-compatible provider configs: (env_prefix, default_base_url, default_model)
_CLOUD_PROVIDERS: dict[str, tuple[str, str, str]] = {
    "openai":   ("OPENAI",   "https://api.openai.com/v1",            "gpt-4o"),
    "deepseek": ("DEEPSEEK", "https://api.deepseek.com/v1",          "deepseek-chat"),
    "qwen":     ("QWEN",     "https://dashscope.aliyuncs.com/compatible-mode/v1", "qwen-plus"),
}


def _cloud_config(provider: str) -> tuple[str, str, str]:
    """Return (api_key, base_url, model) for a cloud provider."""
    prefix, default_url, default_model = _CLOUD_PROVIDERS[provider]
    api_key = os.getenv(f"{prefix}_API_KEY", "")
    base_url = os.getenv(f"{prefix}_BASE_URL", default_url)
    model = os.getenv(f"{prefix}_MODEL", default_model)
    return api_key, base_url, model


def get_default_model() -> str:
    """Return the default model name for the active provider."""
    if LLM_PROVIDER == "ollama":
        return OLLAMA_MODEL
    if LLM_PROVIDER in _CLOUD_PROVIDERS:
        _, _, model = _cloud_config(LLM_PROVIDER)
        return model
    return OLLAMA_MODEL


def get_provider_info() -> dict:
    """Return provider metadata for health/status endpoints."""
    info: dict = {"provider": LLM_PROVIDER, "model": get_default_model()}
    if LLM_PROVIDER in _CLOUD_PROVIDERS:
        prefix = _CLOUD_PROVIDERS[LLM_PROVIDER][0]
        info["has_api_key"] = bool(os.getenv(f"{prefix}_API_KEY"))
    # List all configured providers
    available = ["ollama"]
    for name in _CLOUD_PROVIDERS:
        prefix = _CLOUD_PROVIDERS[name][0]
        if os.getenv(f"{prefix}_API_KEY"):
            available.append(name)
    info["available_providers"] = available
    return info


# ---------- Ollama implementation ----------

async def _ollama_generate(prompt: str, model: str, temperature: Optional[float]) -> dict:
    payload: dict = {"model": model, "prompt": prompt, "stream": False, "think": False}
    if temperature is not None:
        payload["options"] = {"temperature": temperature}
    async with httpx.AsyncClient(timeout=120.0) as client:
        resp = await client.post(f"{OLLAMA_BASE_URL}/api/generate", json=payload)
        resp.raise_for_status()
        data = resp.json()
        return {"text": data.get("response", ""), "token_count": data.get("eval_count", 0)}


async def _ollama_generate_stream(prompt: str, model: str, temperature: Optional[float]) -> AsyncGenerator[str, None]:
    payload: dict = {"model": model, "prompt": prompt, "stream": True, "think": False}
    if temperature is not None:
        payload["options"] = {"temperature": temperature}
    async with httpx.AsyncClient(timeout=120.0) as client:
        async with client.stream("POST", f"{OLLAMA_BASE_URL}/api/generate", json=payload) as resp:
            resp.raise_for_status()
            async for line in resp.aiter_lines():
                if line.strip():
                    chunk = json.loads(line)
                    token = chunk.get("response", "")
                    if token:
                        yield token
                    if chunk.get("done", False):
                        break


async def _ollama_list_models() -> list[str]:
    async with httpx.AsyncClient(timeout=10.0) as client:
        resp = await client.get(f"{OLLAMA_BASE_URL}/api/tags")
        resp.raise_for_status()
        data = resp.json()
        return [m.get("name", "") for m in data.get("models", []) if m.get("name")]


# ---------- OpenAI-compatible implementation ----------

async def _openai_generate(prompt: str, provider: str, model: str, temperature: Optional[float]) -> dict:
    api_key, base_url, default_model = _cloud_config(provider)
    if not api_key:
        raise ValueError(f"{provider} API key not configured")
    use_model = model if model != OLLAMA_MODEL else default_model
    headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}
    body: dict = {
        "model": use_model,
        "messages": [{"role": "user", "content": prompt}],
    }
    if temperature is not None:
        body["temperature"] = temperature

    async with httpx.AsyncClient(timeout=120.0) as client:
        resp = await client.post(f"{base_url}/chat/completions", json=body, headers=headers)
        resp.raise_for_status()
        data = resp.json()
        choice = data.get("choices", [{}])[0]
        text = choice.get("message", {}).get("content", "")
        usage = data.get("usage", {})
        token_count = usage.get("completion_tokens", 0) or usage.get("total_tokens", 0)
        return {"text": text, "token_count": token_count}


async def _openai_generate_stream(prompt: str, provider: str, model: str, temperature: Optional[float]) -> AsyncGenerator[str, None]:
    api_key, base_url, default_model = _cloud_config(provider)
    if not api_key:
        raise ValueError(f"{provider} API key not configured")
    use_model = model if model != OLLAMA_MODEL else default_model
    headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}
    body: dict = {
        "model": use_model,
        "messages": [{"role": "user", "content": prompt}],
        "stream": True,
    }
    if temperature is not None:
        body["temperature"] = temperature

    async with httpx.AsyncClient(timeout=120.0) as client:
        async with client.stream("POST", f"{base_url}/chat/completions", json=body, headers=headers) as resp:
            resp.raise_for_status()
            async for line in resp.aiter_lines():
                line = line.strip()
                if not line.startswith("data: "):
                    continue
                payload = line[6:]
                if payload == "[DONE]":
                    break
                try:
                    chunk = json.loads(payload)
                    delta = chunk.get("choices", [{}])[0].get("delta", {})
                    token = delta.get("content", "")
                    if token:
                        yield token
                except json.JSONDecodeError:
                    continue


async def _openai_list_models(provider: str) -> list[str]:
    api_key, base_url, _ = _cloud_config(provider)
    if not api_key:
        return []
    headers = {"Authorization": f"Bearer {api_key}"}
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            resp = await client.get(f"{base_url}/models", headers=headers)
            resp.raise_for_status()
            data = resp.json()
            return [m.get("id", "") for m in data.get("data", []) if m.get("id")]
    except Exception:
        # Some providers don't support /models endpoint; return default only
        _, _, default_model = _cloud_config(provider)
        return [default_model]


# ---------- Unified interface ----------

async def generate(prompt: str, model: str = "", temperature: Optional[float] = None) -> dict:
    """Non-streaming generation. Returns {"text": ..., "token_count": ...}."""
    provider = LLM_PROVIDER
    effective_model = model or get_default_model()
    logger.info("generate: provider=%s model=%s prompt_len=%d", provider, effective_model, len(prompt))

    if provider == "ollama":
        return await _ollama_generate(prompt, effective_model, temperature)
    if provider in _CLOUD_PROVIDERS:
        return await _openai_generate(prompt, provider, effective_model, temperature)
    # Fallback to ollama
    return await _ollama_generate(prompt, effective_model, temperature)


async def generate_stream(prompt: str, model: str = "", temperature: Optional[float] = None) -> AsyncGenerator[str, None]:
    """Streaming generation. Yields tokens."""
    provider = LLM_PROVIDER
    effective_model = model or get_default_model()
    logger.info("generate_stream: provider=%s model=%s prompt_len=%d", provider, effective_model, len(prompt))

    if provider == "ollama":
        async for token in _ollama_generate_stream(prompt, effective_model, temperature):
            yield token
    elif provider in _CLOUD_PROVIDERS:
        async for token in _openai_generate_stream(prompt, provider, effective_model, temperature):
            yield token
    else:
        async for token in _ollama_generate_stream(prompt, effective_model, temperature):
            yield token


async def list_models() -> list[str]:
    """List available models for the active provider."""
    if LLM_PROVIDER == "ollama":
        return await _ollama_list_models()
    if LLM_PROVIDER in _CLOUD_PROVIDERS:
        return await _openai_list_models(LLM_PROVIDER)
    return await _ollama_list_models()
