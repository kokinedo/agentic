"""Synthesizer agent — produces a coherent answer from research findings."""

from __future__ import annotations

import json
import re
from typing import Any

from agentic.agents.base import BaseAgent
from agentic.models import ResearchFindings, SynthesizedAnswer


class Synthesizer(BaseAgent):
    """Synthesizes research findings into a coherent, sourced answer."""

    name = "Synthesizer"
    color = "green"

    async def run(
        self, question: str, findings: list[ResearchFindings]
    ) -> SynthesizedAnswer:
        """Synthesize findings into a final answer."""
        await self._emit("thinking", "Synthesizing research findings...")

        # Format findings into context
        context_parts: list[str] = []
        all_sources: list[str] = []
        for finding in findings:
            context_parts.append(
                f"Research on: {finding.query}\n"
                f"Summary: {finding.summary}\n"
                f"Sources: {', '.join(finding.sources)}"
            )
            all_sources.extend(finding.sources)

        context = "\n\n---\n\n".join(context_parts)

        system = (
            "You are a research synthesizer. Given research findings, produce a "
            "comprehensive, well-structured answer. Return a JSON object wrapped in "
            "```json ... ``` with these keys:\n"
            '- "answer": a thorough markdown-formatted answer\n'
            '- "key_points": a list of 3-7 key takeaway strings\n'
            '- "sources": list of source URLs used\n'
            '- "confidence": one of "high", "medium", or "low"\n'
        )
        prompt = (
            f"Question: {question}\n\n"
            f"Research findings:\n{context}\n\n"
            "Synthesize into a final answer as JSON."
        )

        response = await self._stream_response(
            system=system,
            messages=[{"role": "user", "content": prompt}],
        )

        # Parse response
        answer = self._parse_response(response, all_sources)
        await self._emit("done")
        return answer

    def _parse_response(
        self, text: str, fallback_sources: list[str]
    ) -> SynthesizedAnswer:
        """Extract SynthesizedAnswer from LLM JSON."""
        match = re.search(r"```json\s*(.*?)\s*```", text, re.DOTALL)
        raw = match.group(1) if match else text

        try:
            data = json.loads(raw)
            return SynthesizedAnswer(
                answer=data.get("answer", text),
                key_points=data.get("key_points", []),
                sources=data.get("sources", fallback_sources),
                confidence=data.get("confidence", "medium"),
            )
        except (json.JSONDecodeError, TypeError):
            return SynthesizedAnswer(
                answer=text,
                key_points=[],
                sources=list(set(fallback_sources)),
                confidence="medium",
            )
