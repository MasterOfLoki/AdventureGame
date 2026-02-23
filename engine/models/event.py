"""Event, condition, and effect models."""

from __future__ import annotations

from pydantic import BaseModel, Field

from engine.models.enums import ConditionType, EffectType, TriggerType


class Condition(BaseModel):
    """A condition that must be met for an event to fire."""
    type: ConditionType
    target: str = ""
    value: str | int | bool = ""


class Effect(BaseModel):
    """An effect applied when an event fires."""
    type: EffectType
    target: str = ""
    value: str | int | bool = ""


class Event(BaseModel):
    """A game event triggered by actions or state changes."""
    id: str
    trigger: TriggerType
    conditions: list[Condition] = Field(default_factory=list)
    effects: list[Effect] = Field(default_factory=list)
    once: bool = False
    priority: int = 0
