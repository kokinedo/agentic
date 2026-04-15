"""Orchestrator — coordinates the multi-agent research loop."""

from __future__ import annotations

import asyncio

from rich.console import Console

from agentic.agents.critic import Critic
from agentic.agents.researcher import Researcher
from agentic.agents.synthesizer import Synthesizer
from agentic.models import (
    AgentEvent,
    Depth,
    ResearchSession,
)
from agentic.providers.base import Provider
from agentic.search import TavilySearch
from agentic.ui.display import ResearchDisplay


class Orchestrator:
    """Coordinates the Researcher -> Synthesizer -> Critic loop."""

    def __init__(self, model: str, depth: Depth, provider: Provider) -> None:
        self.model = model
        self.depth = depth
        self._event_queue: asyncio.Queue[AgentEvent] = asyncio.Queue()
        self._search = TavilySearch()

        self._researcher = Researcher(
            model=model,
            provider=provider,
            event_queue=self._event_queue,
            search=self._search,
        )
        self._synthesizer = Synthesizer(
            model=model,
            provider=provider,
            event_queue=self._event_queue,
        )
        self._critic = Critic(
            model=model,
            provider=provider,
            event_queue=self._event_queue,
        )

    async def run(self, question: str, console: Console) -> ResearchSession:
        """Run the full research pipeline."""
        session = ResearchSession(
            question=question,
            depth=self.depth,
            model=self.model,
        )

        done_event = asyncio.Event()
        display = ResearchDisplay(question, console)
        display_task = asyncio.create_task(
            display.run(self._event_queue, done_event)
        )

        try:
            follow_up_queries: list[str] = []

            for cycle in range(self.depth.value):
                # Emit orchestrator status
                await self._event_queue.put(
                    AgentEvent(
                        agent_name="Orchestrator",
                        event_type="thinking",
                        content=f"Cycle {cycle + 1}/{self.depth.value}",
                    )
                )

                # Research phase
                if follow_up_queries:
                    combined_question = (
                        f"{question}\n\nAdditional areas to investigate:\n"
                        + "\n".join(f"- {q}" for q in follow_up_queries)
                    )
                else:
                    combined_question = question

                findings = await self._researcher.run(combined_question)
                session.findings.append(findings)

                # Synthesis phase
                synthesis = await self._synthesizer.run(question, session.findings)
                session.synthesis = synthesis

                # Critique phase
                critique = await self._critic.run(question, synthesis, session.findings)
                session.critique = critique

                if critique.approved or cycle == self.depth.value - 1:
                    break

                follow_up_queries = critique.follow_up_queries

            # Finalize
            session.final_answer = (
                session.synthesis.answer if session.synthesis else ""
            )

        finally:
            done_event.set()
            await display_task

        return session
