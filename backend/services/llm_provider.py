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
import re
from typing import AsyncGenerator, Optional

import httpx

logger = logging.getLogger("app.llm")


def _strip_trailing_instruction(prompt: str) -> str:
    """Remove trailing '请直接/只输出xxx：' that chat models tend to echo."""
    return re.sub(r"\n*请[直接只]*输出[^\n]*[：:]\s*$", "", prompt)


# Markers that separate "instructions" from "user content" in our prompts.
_CONTENT_MARKERS = ["主题/大纲：\n", "主题：", "原文：\n", "请创作："]

# Trailing instruction patterns to strip from user content portion.
_TRAILING_RE = re.compile(
    r"\n+(?:请[^\n]*[：:]|翻译结果[：:]|润色后的文本[：:]|摘要[：:])\s*$"
)


def _prompt_to_messages(prompt: str) -> list[dict]:
    """Split a single prompt into system + user chat messages.

    Looks for content markers (主题：, 原文：, etc.) and splits the prompt so
    that instructions go into the system message and the actual user content
    goes into the user message.  This prevents chat models from echoing the
    prompt structure back in their output.
    """
    best_pos = -1
    best_marker = ""
    for marker in _CONTENT_MARKERS:
        pos = prompt.rfind(marker)
        if pos > best_pos:
            best_pos = pos
            best_marker = marker

    if best_pos > 0:
        system = prompt[:best_pos].rstrip()
        user_part = prompt[best_pos + len(best_marker) :].strip()
        # Remove trailing output instruction (e.g. "请直接输出xxx：")
        user_part = _TRAILING_RE.sub("", user_part).strip()
        if user_part:
            # Keep the marker prefix so the model knows this is a topic/source text
            marker_label = best_marker.rstrip("\n")  # e.g. "主题：", "原文："
            user_msg = f"{marker_label}{user_part}"
            logger.info("_prompt_to_messages: split at '%s' -> system_len=%d user_len=%d", marker_label, len(system), len(user_msg))
            return [
                {"role": "system", "content": system},
                {"role": "user", "content": user_msg},
            ]

    # Fallback: strip trailing instruction, send as user message
    clean = _strip_trailing_instruction(prompt)
    logger.info("_prompt_to_messages: fallback (no marker found), user_len=%d", len(clean))
    return [{"role": "user", "content": clean}]

# ---------- Provider registry ----------

LLM_PROVIDER = os.getenv("LLM_PROVIDER", "ollama").lower()

# Ollama settings (reuse existing)
OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "qwen3.5:9b")
OLLAMA_NUM_GPU = int(os.getenv("OLLAMA_NUM_GPU", "99"))  # max layers on GPU
OLLAMA_NUM_PREDICT = int(os.getenv("OLLAMA_NUM_PREDICT", "4096"))  # max tokens to generate

# OpenAI-compatible provider configs: (env_prefix, default_base_url, default_model)
_CLOUD_PROVIDERS: dict[str, tuple[str, str, str]] = {
    "openai":   ("OPENAI",   "https://api.openai.com/v1",            "gpt-4o"),
    "deepseek": ("DEEPSEEK", "https://api.deepseek.com/v1",          "deepseek-chat"),
    "qwen":     ("QWEN",     "https://dashscope.aliyuncs.com/compatible-mode/v1", "qwen-plus"),
    "glm":      ("GLM",      "http://100.80.20.2:4000/v1",           "meta-llama/Llama-4-Maverick-17B-128E-Instruct"),
    "mm":       ("MM",       "http://100.80.20.5:4001/v1",           "meta-llama/Llama-3.1-8B-Instruct"),
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
        key = os.getenv(f"{prefix}_API_KEY", "")
        if key:
            available.append(name)
    info["available_providers"] = available
    return info


# ---------- Model-to-provider routing ----------

def _build_model_provider_map() -> dict[str, str]:
    """Build a mapping from model name to provider name for all configured providers."""
    mapping: dict[str, str] = {}
    for name, (prefix, _, default_model) in _CLOUD_PROVIDERS.items():
        key = os.getenv(f"{prefix}_API_KEY", "")
        if key:
            mapping[default_model] = name
    return mapping


def _resolve_provider(model: str) -> str:
    """Given a model name, find the best provider for it."""
    model_map = _build_model_provider_map()
    if model in model_map:
        return model_map[model]
    return LLM_PROVIDER


# ---------- Ollama implementation ----------

async def _ollama_generate(prompt: str, model: str, temperature: Optional[float]) -> dict:
    options: dict = {"num_gpu": OLLAMA_NUM_GPU, "num_predict": OLLAMA_NUM_PREDICT}
    if temperature is not None:
        options["temperature"] = temperature
    messages = _prompt_to_messages(prompt)
    payload: dict = {
        "model": model,
        "messages": messages,
        "stream": False,
        "think": False,
        "options": options,
    }
    async with httpx.AsyncClient(timeout=300.0) as client:
        resp = await client.post(f"{OLLAMA_BASE_URL}/api/chat", json=payload)
        resp.raise_for_status()
        data = resp.json()
        text = data.get("message", {}).get("content", "")
        return {"text": text, "token_count": data.get("eval_count", 0)}


async def _ollama_generate_stream(prompt: str, model: str, temperature: Optional[float]) -> AsyncGenerator[str, None]:
    options: dict = {"num_gpu": OLLAMA_NUM_GPU, "num_predict": OLLAMA_NUM_PREDICT}
    if temperature is not None:
        options["temperature"] = temperature
    messages = _prompt_to_messages(prompt)
    payload: dict = {
        "model": model,
        "messages": messages,
        "stream": True,
        "think": False,
        "options": options,
    }
    async with httpx.AsyncClient(timeout=300.0) as client:
        async with client.stream("POST", f"{OLLAMA_BASE_URL}/api/chat", json=payload) as resp:
            resp.raise_for_status()
            async for line in resp.aiter_lines():
                if line.strip():
                    chunk = json.loads(line)
                    token = chunk.get("message", {}).get("content", "")
                    if token:
                        yield token
                    if chunk.get("done", False):
                        break


# Models that are not suitable for text generation (e.g. OCR, embedding)
_EXCLUDED_MODELS = {"deepseek-ocr", "nomic-embed", "all-minilm", "snowflake-arctic-embed"}


async def _ollama_list_models() -> list[str]:
    async with httpx.AsyncClient(timeout=10.0) as client:
        resp = await client.get(f"{OLLAMA_BASE_URL}/api/tags")
        resp.raise_for_status()
        data = resp.json()
        names = [m.get("name", "") for m in data.get("models", []) if m.get("name")]
        return [n for n in names if not any(ex in n for ex in _EXCLUDED_MODELS)]


# ---------- OpenAI-compatible implementation ----------

async def _openai_generate(prompt: str, provider: str, model: str, temperature: Optional[float]) -> dict:
    api_key, base_url, default_model = _cloud_config(provider)
    if not api_key:
        raise ValueError(f"{provider} API key not configured")
    use_model = model if model != OLLAMA_MODEL else default_model
    headers: dict[str, str] = {"Content-Type": "application/json"}
    if api_key and api_key != "EMPTY":
        headers["Authorization"] = f"Bearer {api_key}"
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
    headers: dict[str, str] = {"Content-Type": "application/json"}
    if api_key and api_key != "EMPTY":
        headers["Authorization"] = f"Bearer {api_key}"
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
    headers: dict[str, str] = {}
    if api_key and api_key != "EMPTY":
        headers["Authorization"] = f"Bearer {api_key}"
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
    effective_model = model or get_default_model()
    provider = _resolve_provider(effective_model)
    logger.info("generate: provider=%s model=%s prompt_len=%d", provider, effective_model, len(prompt))

    if provider == "ollama":
        return await _ollama_generate(prompt, effective_model, temperature)
    if provider in _CLOUD_PROVIDERS:
        return await _openai_generate(prompt, provider, effective_model, temperature)
    # Fallback to ollama
    return await _ollama_generate(prompt, effective_model, temperature)


async def generate_stream(prompt: str, model: str = "", temperature: Optional[float] = None) -> AsyncGenerator[str, None]:
    """Streaming generation. Yields tokens."""
    effective_model = model or get_default_model()
    provider = _resolve_provider(effective_model)
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
    """List available models from all configured providers."""
    all_models: list[str] = []
    # Collect models from the active provider first
    if LLM_PROVIDER == "ollama":
        try:
            all_models.extend(await _ollama_list_models())
        except Exception:
            pass
    elif LLM_PROVIDER in _CLOUD_PROVIDERS:
        try:
            all_models.extend(await _openai_list_models(LLM_PROVIDER))
        except Exception:
            _, _, default_model = _cloud_config(LLM_PROVIDER)
            all_models.append(default_model)
    # Also collect models from other configured providers
    for name in _CLOUD_PROVIDERS:
        if name == LLM_PROVIDER:
            continue
        prefix = _CLOUD_PROVIDERS[name][0]
        if os.getenv(f"{prefix}_API_KEY", ""):
            try:
                provider_models = await _openai_list_models(name)
                all_models.extend(m for m in provider_models if m not in all_models)
            except Exception:
                _, _, default_model = _cloud_config(name)
                if default_model not in all_models:
                    all_models.append(default_model)
    return all_models
