"""Abstract base agent with shared streaming logic."""

from __future__ import annotations

import asyncio
from abc import ABC, abstractmethod
from typing import Any

from agentic.models import AgentEvent
from agentic.providers.base import Provider


class BaseAgent(ABC):
    """Base class for all agents."""

    name: str = "Agent"
    color: str = "white"

    def __init__(
        self,
        model: str,
        provider: Provider,
        event_queue: asyncio.Queue[AgentEvent],
    ) -> None:
        self.model = model
        self._provider = provider
        self._event_queue = event_queue

    async def _emit(self, event_type: str, content: str = "") -> None:
        """Push an event onto the shared queue."""
        event = AgentEvent(
            agent_name=self.name,
            event_type=event_type,  # type: ignore[arg-type]
            content=content,
        )
        await self._event_queue.put(event)

    async def _stream_response(self, system: str, messages: list[dict[str, Any]]) -> str:
        """Stream a response from the provider and emit streaming events."""
        full_text = ""
        async for text in self._provider.stream(system, messages, self.model):
            full_text += text
            await self._emit("streaming", text)
        return full_text

    @abstractmethod
    async def run(self, *args: Any, **kwargs: Any) -> Any:
        """Execute the agent's main task."""
        ...
