"""Claude (Anthropic) provider."""

from __future__ import annotations

from typing import AsyncIterator

from anthropic import AsyncAnthropic

from agentic.providers.base import Provider


class ClaudeProvider(Provider):
    """Anthropic Claude provider using the official SDK."""

    def __init__(self, api_key: str) -> None:
        self._client = AsyncAnthropic(api_key=api_key)

    def name(self) -> str:
        return "claude"

    def default_model(self) -> str:
        return "claude-sonnet-4-20250514"

    async def stream(self, system: str, messages: list[dict], model: str) -> AsyncIterator[str]:
        async with self._client.messages.stream(
            model=model,
            max_tokens=4096,
            system=system,
            messages=messages,
        ) as stream:
            async for text in stream.text_stream:
                yield text
