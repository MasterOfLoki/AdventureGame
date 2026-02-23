"""Game object models."""

from __future__ import annotations

from pydantic import BaseModel, Field

from engine.models.enums import ObjectProperty


class ObjectDescription(BaseModel):
    """Description variants for an object."""
    room: str = ""
    examine: str = ""
    on_open: str | None = None
    on_read: str | None = None


class GameObject(BaseModel):
    """An interactive object in the game world."""
    id: str
    name: str
    aliases: list[str] = Field(default_factory=list)
    description: ObjectDescription = Field(default_factory=ObjectDescription)
    location: str | None = None
    parent_object: str | None = None
    properties: list[ObjectProperty] = Field(default_factory=list)
    size: int = 1
    capacity: int = 0
    key_id: str | None = None
    damage: int = 0
    light_fuel: int = -1
    score_value: int = 0
    initial_properties: list[ObjectProperty] | None = None
