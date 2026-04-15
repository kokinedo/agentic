"""Rich Live multi-panel display for research progress."""

from __future__ import annotations

import asyncio
from collections import defaultdict

from rich.console import Console
from rich.layout import Layout
from rich.live import Live
from rich.panel import Panel
from rich.text import Text

from agentic.models import AgentEvent
from agentic.ui.theme import AGENT_COLORS, LOGO


class ResearchDisplay:
    """Real-time multi-panel display showing agent activity."""

    MAX_LOG_LINES = 20

    def __init__(self, question: str, console: Console) -> None:
        self._question = question
        self._console = console
        self._agent_logs: dict[str, list[str]] = defaultdict(list)
        self._agent_status: dict[str, str] = {
            "Researcher": "idle",
            "Synthesizer": "idle",
            "Critic": "idle",
        }
        self._wide = (console.width or 120) >= 100

    def _truncate_logs(self, agent: str) -> None:
        logs = self._agent_logs[agent]
        if len(logs) > self.MAX_LOG_LINES:
            self._agent_logs[agent] = logs[-self.MAX_LOG_LINES :]

    def handle_event(self, event: AgentEvent) -> None:
        """Process an agent event and update internal state."""
        name = event.agent_name

        if event.event_type == "streaming":
            # Append to current line incrementally
            logs = self._agent_logs[name]
            if logs and self._agent_status.get(name) == "streaming":
                logs[-1] += event.content
            else:
                logs.append(event.content)
            self._agent_status[name] = "streaming"
        elif event.event_type == "thinking":
            self._agent_logs[name].append(f"[dim]Thinking...[/dim]")
            self._agent_status[name] = "thinking"
        elif event.event_type == "searching":
            self._agent_logs[name].append(f"[yellow]Searching:[/yellow] {event.content}")
            self._agent_status[name] = "searching"
        elif event.event_type == "done":
            self._agent_logs[name].append(f"[green]Done[/green]")
            self._agent_status[name] = "done"
        elif event.event_type == "error":
            self._agent_logs[name].append(f"[red]Error: {event.content}[/red]")
            self._agent_status[name] = "error"

        self._truncate_logs(name)

    def _make_agent_panel(self, name: str) -> Panel:
        color = AGENT_COLORS.get(name, "white")
        status = self._agent_status.get(name, "idle")
        logs = self._agent_logs.get(name, [])

        # Build content text
        content = Text()
        for line in logs[-15:]:
            content.append_text(Text.from_markup(line + "\n"))

        status_indicator = {
            "idle": "[dim]Idle[/dim]",
            "thinking": "[bold magenta]Thinking...[/bold magenta]",
            "searching": "[bold yellow]Searching...[/bold yellow]",
            "streaming": "[bold cyan]Streaming...[/bold cyan]",
            "done": "[bold green]Complete[/bold green]",
            "error": "[bold red]Error[/bold red]",
        }.get(status, status)

        return Panel(
            content,
            title=f"[bold {color}]{name}[/bold {color}]",
            subtitle=Text.from_markup(status_indicator),
            border_style=color,
            height=20,
        )

    def _build_layout(self) -> Layout:
        layout = Layout()

        # Header
        header_text = Text.from_markup(
            f"[bold cyan]{LOGO}[/bold cyan]\n"
            f"  [bold white]Research:[/bold white] {self._question}\n"
        )
        header = Layout(Panel(header_text, border_style="blue"), name="header", size=11)

        # Agent panels
        researcher_panel = Layout(self._make_agent_panel("Researcher"), name="researcher")
        synthesizer_panel = Layout(self._make_agent_panel("Synthesizer"), name="synthesizer")
        critic_panel = Layout(self._make_agent_panel("Critic"), name="critic")

        if self._wide:
            agents = Layout(name="agents", size=22)
            agents.split_row(researcher_panel, synthesizer_panel, critic_panel)
        else:
            agents = Layout(name="agents")
            agents.split_column(researcher_panel, synthesizer_panel, critic_panel)

        # Footer status
        statuses = " | ".join(
            f"[{AGENT_COLORS.get(n, 'white')}]{n}: {self._agent_status.get(n, 'idle')}[/{AGENT_COLORS.get(n, 'white')}]"
            for n in ["Researcher", "Synthesizer", "Critic"]
        )
        footer = Layout(
            Panel(Text.from_markup(statuses), border_style="dim"),
            name="footer",
            size=3,
        )

        layout.split_column(header, agents, footer)
        return layout

    async def run(
        self,
        event_queue: asyncio.Queue[AgentEvent],
        done_event: asyncio.Event,
    ) -> None:
        """Main display loop — consume events and refresh at ~8fps."""
        with Live(
            self._build_layout(),
            console=self._console,
            refresh_per_second=8,
            screen=False,
        ) as live:
            while not done_event.is_set():
                # Drain all pending events
                while True:
                    try:
                        event = event_queue.get_nowait()
                        self.handle_event(event)
                    except asyncio.QueueEmpty:
                        break
                live.update(self._build_layout())
                await asyncio.sleep(0.125)  # ~8fps

            # Final drain
            while True:
                try:
                    event = event_queue.get_nowait()
                    self.handle_event(event)
                except asyncio.QueueEmpty:
                    break
            live.update(self._build_layout())
