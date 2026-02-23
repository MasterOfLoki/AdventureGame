"""Terminal I/O with rich library for colored output."""

from __future__ import annotations

from rich.console import Console
from rich.panel import Panel
from rich.text import Text


class TextInterface:
    """Rich-powered terminal interface for the game."""

    def __init__(self, debug: bool = False):
        self.console = Console()
        self.debug = debug

    def show_title(self, title: str):
        self.console.print()
        self.console.print(
            Panel(title, style="bold green", border_style="green")
        )
        self.console.print()

    def show_text(self, text: str):
        if not text:
            return
        self.console.print(text)
        self.console.print()

    def show_room(self, room_text: str):
        if not room_text:
            return
        lines = room_text.split("\n")
        if lines:
            # First line is room name — show bold
            self.console.print(f"[bold cyan]{lines[0]}[/bold cyan]")
            for line in lines[1:]:
                self.console.print(line)
        self.console.print()

    def show_error(self, text: str):
        self.console.print(f"[red]{text}[/red]")
        self.console.print()

    def show_debug(self, text: str):
        if self.debug:
            self.console.print(f"[dim]{text}[/dim]")

    def get_input(self) -> str:
        try:
            result = self.console.input("[bold yellow]> [/bold yellow]")
            return result.strip()
        except EOFError:
            return "quit"
        except KeyboardInterrupt:
            self.console.print()
            return "quit"

    def show_death(self):
        self.console.print()
        self.console.print("[bold red]   **** You have died ****[/bold red]")
        self.console.print()

    def show_score(self, score: int, max_score: int, turns: int, rank: str):
        self.console.print(
            f"Your score is {score} (out of {max_score}), in {turns} turns."
        )
        self.console.print(f"This gives you the rank of {rank}.")
        self.console.print()
