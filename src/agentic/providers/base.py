"""Abstract provider interface."""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import AsyncIterator


class Provider(ABC):
    """Base class for LLM providers."""

    @abstractmethod
    async def stream(self, system: str, messages: list[dict], model: str) -> AsyncIterator[str]:
        """Stream text chunks from the LLM."""
        ...

    @abstractmethod
    def default_model(self) -> str:
        """Return the default model name for this provider."""
        ...

    @abstractmethod
    def name(self) -> str:
        """Return the provider name."""
        ...
