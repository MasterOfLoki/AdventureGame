"""Verb definition models."""

from __future__ import annotations

from pydantic import BaseModel, Field


class VerbSyntax(BaseModel):
    """Defines valid syntax patterns for a verb."""
    pattern: str
    prepositions: list[str] = Field(default_factory=list)
    requires_direct_object: bool = False
    requires_indirect_object: bool = False


class VerbDefinition(BaseModel):
    """Definition of a game verb/action."""
    id: str
    names: list[str] = Field(default_factory=list)
    syntax: list[VerbSyntax] = Field(default_factory=list)
    description: str = ""
    requires_object_property: str | None = None
