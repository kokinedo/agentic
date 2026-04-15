"""Theme constants for the agentic UI."""

from __future__ import annotations

AGENT_COLORS: dict[str, str] = {
    "Researcher": "cyan",
    "Synthesizer": "green",
    "Critic": "red",
    "Orchestrator": "yellow",
}

LOGO = r"""
   ___    ____  ____  _   _ _____ ___  ____
  / _ \  / ___|| ___|| \ | |_   _|_ _|/ ___|
 / /_\ \| |  _ |  _| |  \| | | |  | || |
 / ___  \| |_| || |___| |\  | | |  | || |___
/_/   \_\\____||_____|_| \_| |_| |___|\____|
"""

STYLE_HEADER = "bold white on blue"
STYLE_BORDER = "dim"
STYLE_STATUS_ACTIVE = "bold green"
STYLE_STATUS_IDLE = "dim white"
STYLE_STATUS_ERROR = "bold red"
