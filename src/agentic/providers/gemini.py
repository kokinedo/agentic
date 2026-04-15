"""Google Gemini provider using raw HTTP."""

from __future__ import annotations

import json
from typing import AsyncIterator

import httpx

from agentic.providers.base import Provider

GEMINI_STREAM_URL = "https://generativelanguage.googleapis.com/v1/models/{model}:streamGenerateContent"


class GeminiProvider(Provider):
    """Google Gemini provider via REST API."""

    def __init__(self, api_key: str) -> None:
        self._api_key = api_key

    def name(self) -> str:
        return "gemini"

    def default_model(self) -> str:
        return "gemini-2.0-flash"

    async def stream(self, system: str, messages: list[dict], model: str) -> AsyncIterator[str]:
        url = GEMINI_STREAM_URL.format(model=model)

        contents = []
        for msg in messages:
            role = "user" if msg["role"] == "user" else "model"
            contents.append({"role": role, "parts": [{"text": msg["content"]}]})

        body = {
            "contents": contents,
            "systemInstruction": {"parts": [{"text": system}]},
        }

        async with httpx.AsyncClient(timeout=60.0) as client:
            async with client.stream(
                "POST",
                url,
                params={"alt": "sse", "key": self._api_key},
                json=body,
            ) as response:
                response.raise_for_status()
                async for line in response.aiter_lines():
                    if not line.startswith("data: "):
                        continue
                    data = line[6:]
                    if data.strip() == "[DONE]":
                        break
                    try:
                        parsed = json.loads(data)
                        candidates = parsed.get("candidates", [])
                        if candidates:
                            parts = candidates[0].get("content", {}).get("parts", [])
                            for part in parts:
                                text = part.get("text", "")
                                if text:
                                    yield text
                    except json.JSONDecodeError:
                        continue
