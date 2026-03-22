import httpx
from typing import AsyncGenerator, Optional

OLLAMA_BASE_URL = "http://localhost:11434"
DEFAULT_MODEL = "qwen3.5:9b"


async def generate(prompt: str, model: str = DEFAULT_MODEL, temperature: Optional[float] = None) -> dict:
    """非流式调用 Ollama，返回完整结果。"""
    payload: dict = {
        "model": model,
        "prompt": prompt,
        "stream": False,
        "think": False,
    }
    if temperature is not None:
        payload["options"] = {"temperature": temperature}
    async with httpx.AsyncClient(timeout=120.0) as client:
        resp = await client.post(f"{OLLAMA_BASE_URL}/api/generate", json=payload)
        resp.raise_for_status()
        data = resp.json()
        return {
            "text": data.get("response", ""),
            "token_count": data.get("eval_count", 0),
        }


async def generate_stream(prompt: str, model: str = DEFAULT_MODEL, temperature: Optional[float] = None) -> AsyncGenerator[str, None]:
    """流式调用 Ollama，逐步返回文本。"""
    payload: dict = {
        "model": model,
        "prompt": prompt,
        "stream": True,
        "think": False,
    }
    if temperature is not None:
        payload["options"] = {"temperature": temperature}
    async with httpx.AsyncClient(timeout=120.0) as client:
        async with client.stream(
            "POST",
            f"{OLLAMA_BASE_URL}/api/generate",
            json=payload,
        ) as resp:
            resp.raise_for_status()
            import json
            async for line in resp.aiter_lines():
                if line.strip():
                    chunk = json.loads(line)
                    token = chunk.get("response", "")
                    if token:
                        yield token
                    if chunk.get("done", False):
                        break
