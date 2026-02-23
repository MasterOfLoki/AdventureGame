"""Abstract base class for parsers."""

from __future__ import annotations

from abc import ABC, abstractmethod

from engine.models.command import ParsedCommand


class ParserContext:
    """Context provided to parsers for disambiguation."""

    def __init__(
        self,
        visible_objects: list[str] | None = None,
        inventory: list[str] | None = None,
        exits: list[str] | None = None,
        valid_verbs: list[str] | None = None,
        npc_names: list[str] | None = None,
    ):
        self.visible_objects = visible_objects or []
        self.inventory = inventory or []
        self.exits = exits or []
        self.valid_verbs = valid_verbs or []
        self.npc_names = npc_names or []


class ParserInterface(ABC):
    """Abstract interface for natural language parsers."""

    @abstractmethod
    def parse(self, input_text: str, context: ParserContext) -> ParsedCommand:
        """Parse natural language input into a structured command."""
        ...
