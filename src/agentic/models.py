"""Data models for the agentic research system."""

from __future__ import annotations

import time
from dataclasses import dataclass, field
from enum import Enum
from typing import Literal


class Depth(Enum):
    """Research depth levels."""

    SHALLOW = 1
    MEDIUM = 2
    DEEP = 3


@dataclass
class SearchResult:
    """A single search result."""

    url: str
    title: str
    content: str
    score: float


@dataclass
class ResearchFindings:
    """Collected research findings from the Researcher agent."""

    query: str
    results: list[SearchResult]
    summary: str
    sources: list[str]


@dataclass
class SynthesizedAnswer:
    """A synthesized answer from the Synthesizer agent."""

    answer: str
    key_points: list[str]
    sources: list[str]
    confidence: str


@dataclass
class CritiqueResult:
    """Critique from the Critic agent."""

    assessment: str
    gaps: list[str]
    follow_up_queries: list[str]
    approved: bool


@dataclass
class AgentEvent:
    """An event emitted by an agent for the UI."""

    agent_name: str
    event_type: Literal["thinking", "searching", "streaming", "done", "error"]
    content: str
    timestamp: float = field(default_factory=time.time)


@dataclass
class ResearchSession:
    """A complete research session."""

    question: str
    depth: Depth
    model: str
    findings: list[ResearchFindings] = field(default_factory=list)
    synthesis: SynthesizedAnswer | None = None
    critique: CritiqueResult | None = None
    final_answer: str = ""
