"""Action handler protocol and result type."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Protocol

from engine.models.command import ParsedCommand
from engine.state.game_state import GameState
from engine.world.world import World


@dataclass
class ActionResult:
    """Result of executing an action."""
    message: str = ""
    success: bool = True
    blocked: bool = False
    extra_messages: list[str] = field(default_factory=list)

    @property
    def full_message(self) -> str:
        parts = [self.message] + self.extra_messages
        return "\n".join(p for p in parts if p)


class ActionHandler(Protocol):
    """Protocol for action handler functions."""

    def __call__(
        self,
        command: ParsedCommand,
        state: GameState,
        world: World,
    ) -> ActionResult: ...
