"""Critic agent — evaluates synthesized answers for accuracy and gaps."""

from __future__ import annotations

import json
import re

from agentic.agents.base import BaseAgent
from agentic.models import CritiqueResult, ResearchFindings, SynthesizedAnswer


class Critic(BaseAgent):
    """Evaluates answers for accuracy, completeness, and bias."""

    name = "Critic"
    color = "red"

    async def run(
        self,
        question: str,
        answer: SynthesizedAnswer,
        findings: list[ResearchFindings],
    ) -> CritiqueResult:
        """Critique the synthesized answer."""
        await self._emit("thinking", "Evaluating answer quality...")

        sources_summary = "\n".join(
            f"- {f.query}: {len(f.results)} results, {len(f.sources)} sources"
            for f in findings
        )

        system = (
            "You are a critical research reviewer. Evaluate the provided answer for:\n"
            "1. Factual accuracy based on the sources\n"
            "2. Completeness — are there gaps?\n"
            "3. Potential bias or one-sided presentation\n"
            "4. Whether follow-up research is needed\n\n"
            "Return a JSON object wrapped in ```json ... ``` with:\n"
            '- "assessment": a detailed text assessment\n'
            '- "gaps": list of identified gaps or weaknesses\n'
            '- "follow_up_queries": list of suggested follow-up search queries (empty if none needed)\n'
            '- "approved": boolean — true if the answer is good enough, false if more research needed\n'
        )
        prompt = (
            f"Original question: {question}\n\n"
            f"Answer provided:\n{answer.answer}\n\n"
            f"Key points: {json.dumps(answer.key_points)}\n"
            f"Confidence: {answer.confidence}\n\n"
            f"Research sources:\n{sources_summary}\n\n"
            "Provide your critique as JSON."
        )

        response = await self._stream_response(
            system=system,
            messages=[{"role": "user", "content": prompt}],
        )

        result = self._parse_response(response)
        await self._emit("done")
        return result

    def _parse_response(self, text: str) -> CritiqueResult:
        """Extract CritiqueResult from LLM JSON."""
        match = re.search(r"```json\s*(.*?)\s*```", text, re.DOTALL)
        raw = match.group(1) if match else text

        try:
            data = json.loads(raw)
            return CritiqueResult(
                assessment=data.get("assessment", text),
                gaps=data.get("gaps", []),
                follow_up_queries=data.get("follow_up_queries", []),
                approved=data.get("approved", True),
            )
        except (json.JSONDecodeError, TypeError):
            return CritiqueResult(
                assessment=text,
                gaps=[],
                follow_up_queries=[],
                approved=True,
            )
