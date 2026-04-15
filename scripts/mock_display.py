"""Generate SVG screenshots of the agentic TUI in various states."""

from __future__ import annotations

import sys
from pathlib import Path

# Add project src to path so we can import display/theme
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))

from rich.console import Console

from agentic.ui.display import ResearchDisplay

OUTPUT_DIR = Path("/Users/kokinedo/Code/portfoliov2/public/screenshots")
QUESTION = "What are the latest breakthroughs in quantum error correction?"


def make_display(console: Console) -> ResearchDisplay:
    return ResearchDisplay(QUESTION, console)


def screenshot_research_in_progress() -> None:
    """Screenshot 1: Research in progress."""
    console = Console(record=True, width=120, force_terminal=True)
    display = make_display(console)

    # Researcher: searching with partial results
    display._agent_status["Researcher"] = "searching"
    display._agent_logs["Researcher"] = [
        "[dim]Thinking...[/dim]",
        "[yellow]Searching:[/yellow] quantum error correction 2024 breakthroughs",
        "[yellow]Searching:[/yellow] surface code logical qubit advances",
        "[yellow]Searching:[/yellow] topological quantum codes recent results",
        "Found 8 sources across 3 queries",
        "Key finding: Google's Willow chip achieved below-threshold error correction",
        "Key finding: Harvard/QuEra demonstrated 48 logical qubits with reconfigurable atoms",
        "Processing additional results...",
    ]

    # Synthesizer: streaming partial synthesis
    display._agent_status["Synthesizer"] = "streaming"
    display._agent_logs["Synthesizer"] = [
        "[dim]Thinking...[/dim]",
        "Recent breakthroughs in quantum error correction have marked a turning point",
        "for the field. Google's Willow processor demonstrated that increasing the",
        "number of physical qubits in a surface code actually reduces logical error",
        "rates -- crossing the critical threshold that theorists predicted decades ago.",
    ]

    # Critic: idle, no logs
    display._agent_status["Critic"] = "idle"

    layout = display._build_layout()
    console.print(layout)
    svg = console.export_svg(title="agentic")
    out = OUTPUT_DIR / "agentic-research.svg"
    out.write_text(svg)
    print(f"Saved {out}")


def screenshot_critique_cycle() -> None:
    """Screenshot 2: Critique cycle."""
    console = Console(record=True, width=120, force_terminal=True)
    display = make_display(console)

    # Researcher: done
    display._agent_status["Researcher"] = "done"
    display._agent_logs["Researcher"] = [
        "[dim]Thinking...[/dim]",
        "[yellow]Searching:[/yellow] quantum error correction 2024 breakthroughs",
        "[yellow]Searching:[/yellow] surface code logical qubit advances",
        "[yellow]Searching:[/yellow] topological quantum codes recent results",
        "Found 12 sources across 4 queries",
        "Key finding: Google's Willow chip achieved below-threshold error correction",
        "Key finding: Harvard/QuEra demonstrated 48 logical qubits",
        "Key finding: Microsoft announced topological qubit progress",
        "[green]Done[/green]",
    ]

    # Synthesizer: done
    display._agent_status["Synthesizer"] = "done"
    display._agent_logs["Synthesizer"] = [
        "[dim]Thinking...[/dim]",
        "Synthesis complete. Covered 3 major breakthroughs:",
        "  1. Google Willow -- below-threshold surface codes",
        "  2. Harvard/QuEra -- 48 logical qubits via atom arrays",
        "  3. Microsoft -- topological qubit milestone",
        "[green]Done[/green]",
    ]

    # Critic: streaming critique
    display._agent_status["Critic"] = "streaming"
    display._agent_logs["Critic"] = [
        "[dim]Thinking...[/dim]",
        "Evaluating factual accuracy...",
        "[red]Gap:[/red] No mention of IBM's approach to error correction",
        "[red]Gap:[/red] Missing comparison of error rates across platforms",
        "[red]Gap:[/red] No discussion of timeline to fault-tolerant computing",
        "[yellow]Follow-up:[/yellow] IBM quantum error correction progress",
        "[yellow]Follow-up:[/yellow] Error rate benchmarks 2024",
        "Recommendation: Additional research needed on 2 topics",
    ]

    layout = display._build_layout()
    console.print(layout)
    svg = console.export_svg(title="agentic")
    out = OUTPUT_DIR / "agentic-critique.svg"
    out.write_text(svg)
    print(f"Saved {out}")


def screenshot_complete() -> None:
    """Screenshot 3: Final result, all agents done."""
    console = Console(record=True, width=120, force_terminal=True)
    display = make_display(console)

    # Researcher: done
    display._agent_status["Researcher"] = "done"
    display._agent_logs["Researcher"] = [
        "[yellow]Searching:[/yellow] quantum error correction 2024 breakthroughs",
        "[yellow]Searching:[/yellow] surface code logical qubit advances",
        "[yellow]Searching:[/yellow] IBM quantum error correction progress",
        "[yellow]Searching:[/yellow] error rate benchmarks comparison 2024",
        "Found 18 sources across 6 queries",
        "Key finding: Google's Willow chip -- below-threshold error correction",
        "Key finding: Harvard/QuEra -- 48 logical qubits",
        "Key finding: IBM Heron -- improved error mitigation at 133 qubits",
        "All research rounds complete (2 rounds, 6 queries)",
        "[green]Done[/green]",
    ]

    # Synthesizer: done
    display._agent_status["Synthesizer"] = "done"
    display._agent_logs["Synthesizer"] = [
        "Final synthesis complete. Key points:",
        "  1. Google Willow crossed the error-correction threshold",
        "  2. Harvard/QuEra scaled to 48 logical qubits via atom arrays",
        "  3. IBM Heron advanced error mitigation at 133 qubits",
        "  4. Error rates improved 10-100x across all platforms",
        "  5. Fault-tolerant computing now projected for 2028-2030",
        "Word count: 487 | Sources cited: 14",
        "[green]Done[/green]",
    ]

    # Critic: done and approved
    display._agent_status["Critic"] = "done"
    display._agent_logs["Critic"] = [
        "Evaluating factual accuracy... [green]passed[/green]",
        "Evaluating source coverage... [green]passed[/green]",
        "Evaluating balance of perspectives... [green]passed[/green]",
        "All gaps from round 1 addressed",
        "No new gaps identified",
        "[bold green]Approved[/bold green]",
        "[green]Done[/green]",
    ]

    layout = display._build_layout()
    console.print(layout)
    svg = console.export_svg(title="agentic")
    out = OUTPUT_DIR / "agentic-complete.svg"
    out.write_text(svg)
    print(f"Saved {out}")


if __name__ == "__main__":
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    screenshot_research_in_progress()
    screenshot_critique_cycle()
    screenshot_complete()
    print("All screenshots generated.")
