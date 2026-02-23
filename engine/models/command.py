"""Parsed command model - the contract between parser and engine."""

from __future__ import annotations

from pydantic import BaseModel


class ParsedCommand(BaseModel):
    """The structured output from the parser.

    This is the critical contract between the LLM parser and the game engine.
    Its JSON Schema is used to constrain LLM output via structured generation.
    """
    verb: str
    direct_object: str | None = None
    indirect_object: str | None = None
    preposition: str | None = None
    raw_input: str = ""
    direction: str | None = None
