"""Tavily API integration for web search."""

from __future__ import annotations

import asyncio
import os

import httpx

from agentic.models import SearchResult


class TavilySearch:
    """Search the web using the Tavily API."""

    API_URL = "https://api.tavily.com/search"

    def __init__(self, api_key: str | None = None) -> None:
        self.api_key = api_key or os.environ.get("TAVILY_API_KEY", "")
        self._available = bool(self.api_key)

    @property
    def available(self) -> bool:
        return self._available

    async def search(self, query: str, max_results: int = 5) -> list[SearchResult]:
        """Execute a single search query via Tavily."""
        if not self._available:
            return []

        async with httpx.AsyncClient(timeout=30.0) as client:
            try:
                response = await client.post(
                    self.API_URL,
                    json={
                        "api_key": self.api_key,
                        "query": query,
                        "max_results": max_results,
                        "include_answer": False,
                    },
                )
                response.raise_for_status()
                data = response.json()
            except (httpx.HTTPError, Exception):
                return []

        results: list[SearchResult] = []
        for item in data.get("results", []):
            results.append(
                SearchResult(
                    url=item.get("url", ""),
                    title=item.get("title", ""),
                    content=item.get("content", ""),
                    score=item.get("score", 0.0),
                )
            )
        return results

    async def search_multiple(
        self, queries: list[str], max_results: int = 3
    ) -> list[SearchResult]:
        """Run multiple searches concurrently and deduplicate by URL."""
        tasks = [self.search(q, max_results=max_results) for q in queries]
        all_results = await asyncio.gather(*tasks)

        seen_urls: set[str] = set()
        deduped: list[SearchResult] = []
        for result_list in all_results:
            for result in result_list:
                if result.url not in seen_urls:
                    seen_urls.add(result.url)
                    deduped.append(result)
        return deduped
