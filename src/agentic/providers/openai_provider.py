"""OpenAI provider."""

from __future__ import annotations

from typing import AsyncIterator

from agentic.providers.base import Provider


class OpenAIProvider(Provider):
    """OpenAI provider using the official SDK."""

    def __init__(self, api_key: str) -> None:
        try:
            from openai import AsyncOpenAI
        except ImportError:
            raise ImportError(
                "openai package is required for the OpenAI provider. "
                "Install it with: pip install openai"
            )
        self._client = AsyncOpenAI(api_key=api_key)

    def name(self) -> str:
        return "openai"

    def default_model(self) -> str:
        return "gpt-4o"

    async def stream(self, system: str, messages: list[dict], model: str) -> AsyncIterator[str]:
        oai_messages = [{"role": "system", "content": system}]
        for msg in messages:
            oai_messages.append({"role": msg["role"], "content": msg["content"]})

        stream = await self._client.chat.completions.create(
            model=model,
            messages=oai_messages,
            stream=True,
        )
        async for chunk in stream:
            delta = chunk.choices[0].delta if chunk.choices else None
            if delta and delta.content:
                yield delta.content
