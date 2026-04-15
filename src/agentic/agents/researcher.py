"""Researcher agent — decomposes questions and searches the web."""

from __future__ import annotations

import asyncio
import json
import re
from typing import Any

from anthropic import AsyncAnthropic

from agentic.agents.base import BaseAgent
from agentic.models import ResearchFindings, SearchResult
from agentic.search import TavilySearch


class Researcher(BaseAgent):
    """Decomposes a research question into queries, searches, and summarizes."""

    name = "Researcher"
    color = "cyan"

    def __init__(
        self,
        model: str,
        client: AsyncAnthropic,
        event_queue: asyncio.Queue,
        search: TavilySearch,
    ) -> None:
        super().__init__(model, client, event_queue)
        self._search = search

    def _parse_queries(self, text: str) -> list[str]:
        """Extract search queries from LLM JSON output."""
        # Try to find JSON block
        match = re.search(r"```json\s*(.*?)\s*```", text, re.DOTALL)
        raw = match.group(1) if match else text

        try:
            data = json.loads(raw)
            if isinstance(data, list):
                return [str(q) for q in data]
            if isinstance(data, dict) and "queries" in data:
                return [str(q) for q in data["queries"]]
        except (json.JSONDecodeError, TypeError):
            pass

        # Fallback: extract quoted strings
        quoted = re.findall(r'"([^"]+)"', text)
        if quoted:
            return quoted[:5]

        return [text.strip()]

    async def run(self, question: str) -> ResearchFindings:
        """Research a question by decomposing, searching, and summarizing."""
        # Step 1: Decompose into search queries
        await self._emit("thinking", "Decomposing question into search queries...")

        decompose_system = (
            "You are a research assistant. Given a question, generate 3-5 focused "
            "search queries that will help find comprehensive information to answer it. "
            "Return ONLY a JSON object with a 'queries' key containing a list of strings. "
            "Wrap it in ```json ... ``` code fences."
        )
        decompose_response = await self._stream_response(
            system=decompose_system,
            messages=[{"role": "user", "content": question}],
        )

        queries = self._parse_queries(decompose_response)

        # Step 2: Search
        results: list[SearchResult] = []
        if self._search.available:
            for q in queries:
                await self._emit("searching", q)
            results = await self._search.search_multiple(queries)
        else:
            await self._emit("searching", "(no search API — using LLM knowledge only)")

        # Step 3: Summarize findings
        await self._emit("thinking", "Summarizing findings...")

        context_parts: list[str] = []
        for i, r in enumerate(results, 1):
            context_parts.append(
                f"[{i}] {r.title}\n    URL: {r.url}\n    {r.content[:500]}"
            )
        context_text = "\n\n".join(context_parts) if context_parts else "(No search results available.)"

        summary_system = (
            "You are a research analyst. Summarize the search results below into a "
            "clear, comprehensive research brief that addresses the original question. "
            "Cite sources by their number [1], [2], etc."
        )
        summary_prompt = (
            f"Original question: {question}\n\n"
            f"Search results:\n{context_text}\n\n"
            "Provide a thorough research summary."
        )
        summary = await self._stream_response(
            system=summary_system,
            messages=[{"role": "user", "content": summary_prompt}],
        )

        sources = list({r.url for r in results})

        await self._emit("done")

        return ResearchFindings(
            query=question,
            results=results,
            summary=summary,
            sources=sources,
        )
