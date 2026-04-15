"""Multi-provider support for agentic."""

from __future__ import annotations

from agentic.providers.base import Provider
from agentic.providers.claude import ClaudeProvider
from agentic.providers.openai_provider import OpenAIProvider
from agentic.providers.gemini import GeminiProvider

PROVIDERS = {"claude": ClaudeProvider, "openai": OpenAIProvider, "gemini": GeminiProvider}


def get_provider(name: str, api_key: str) -> Provider:
    """Create a provider instance by name."""
    cls = PROVIDERS.get(name)
    if cls is None:
        raise ValueError(f"Unknown provider: {name}. Choose: {', '.join(PROVIDERS)}")
    return cls(api_key)
