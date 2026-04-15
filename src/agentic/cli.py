"""CLI interface for the agentic research system."""

from __future__ import annotations

import asyncio
import json
import os
import sys
from pathlib import Path

import typer
from rich.console import Console
from rich.markdown import Markdown
from rich.panel import Panel
from rich.table import Table
from rich.text import Text

from agentic.models import Depth
from agentic.orchestrator import Orchestrator
from agentic.ui.theme import LOGO

app = typer.Typer(
    name="agentic",
    help="A multi-agent AI research system.",
    add_completion=False,
)

console = Console()

DEPTH_MAP = {
    "shallow": Depth.SHALLOW,
    "medium": Depth.MEDIUM,
    "deep": Depth.DEEP,
}


def _run_research(question: str, depth: Depth, model: str) -> dict:
    """Run the async orchestrator and return session data."""
    orchestrator = Orchestrator(model=model, depth=depth)
    session = asyncio.run(orchestrator.run(question, console))

    return {
        "question": session.question,
        "depth": session.depth.name,
        "model": session.model,
        "final_answer": session.final_answer,
        "key_points": session.synthesis.key_points if session.synthesis else [],
        "confidence": session.synthesis.confidence if session.synthesis else "unknown",
        "sources": session.synthesis.sources if session.synthesis else [],
        "critique": session.critique.assessment if session.critique else "",
        "approved": session.critique.approved if session.critique else False,
        "cycles": len(session.findings),
    }


@app.command()
def research(
    question: str = typer.Argument(..., help="The research question to investigate"),
    depth: str = typer.Option("medium", "--depth", "-d", help="Research depth: shallow, medium, deep"),
    model: str = typer.Option("claude-sonnet-4-20250514", "--model", "-m", help="Claude model to use"),
    output: str | None = typer.Option(None, "--output", "-o", help="Save output to file (markdown or json)"),
) -> None:
    """Research a question using multiple AI agents."""
    # Validate depth
    depth_enum = DEPTH_MAP.get(depth.lower())
    if depth_enum is None:
        console.print(f"[red]Invalid depth '{depth}'. Choose: shallow, medium, deep[/red]")
        raise typer.Exit(code=1)

    # Check API key
    if not os.environ.get("ANTHROPIC_API_KEY"):
        console.print("[red]ANTHROPIC_API_KEY environment variable is required.[/red]")
        raise typer.Exit(code=1)

    if not os.environ.get("TAVILY_API_KEY"):
        console.print("[yellow]Warning: TAVILY_API_KEY not set. Search will be disabled; using LLM knowledge only.[/yellow]")

    # Print logo
    console.print(Text.from_markup(f"[bold cyan]{LOGO}[/bold cyan]"))
    console.print()

    # Run research
    try:
        result = _run_research(question, depth_enum, model)
    except KeyboardInterrupt:
        console.print("\n[yellow]Research interrupted.[/yellow]")
        raise typer.Exit(code=130)
    except Exception as e:
        console.print(f"\n[red]Error: {e}[/red]")
        raise typer.Exit(code=1)

    # Display final answer
    console.print()
    console.print(Panel("[bold]Research Complete[/bold]", border_style="green"))
    console.print()

    console.print(Markdown(result["final_answer"]))
    console.print()

    # Key points
    if result["key_points"]:
        console.print(Panel("[bold]Key Points[/bold]", border_style="cyan"))
        for i, point in enumerate(result["key_points"], 1):
            console.print(f"  [cyan]{i}.[/cyan] {point}")
        console.print()

    # Sources table
    if result["sources"]:
        table = Table(title="Sources", border_style="dim")
        table.add_column("#", style="dim", width=4)
        table.add_column("URL", style="blue")
        for i, src in enumerate(result["sources"], 1):
            table.add_row(str(i), src)
        console.print(table)
        console.print()

    # Meta info
    console.print(
        f"[dim]Confidence: {result['confidence']} | "
        f"Cycles: {result['cycles']} | "
        f"Approved: {result['approved']}[/dim]"
    )

    # Save output
    if output:
        out_path = Path(output)
        if out_path.suffix == ".json":
            out_path.write_text(json.dumps(result, indent=2))
        else:
            md_content = (
                f"# {result['question']}\n\n"
                f"{result['final_answer']}\n\n"
                "## Key Points\n\n"
                + "\n".join(f"- {p}" for p in result["key_points"])
                + "\n\n## Sources\n\n"
                + "\n".join(f"- {s}" for s in result["sources"])
                + "\n"
            )
            out_path.write_text(md_content)
        console.print(f"\n[green]Output saved to {out_path}[/green]")


if __name__ == "__main__":
    app()
