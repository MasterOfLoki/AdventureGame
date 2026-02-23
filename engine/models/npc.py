"""NPC models."""

from __future__ import annotations

from pydantic import BaseModel, Field

from engine.models.enums import NPCAttitude


class NPCBehavior(BaseModel):
    """Behavior configuration for an NPC."""
    wanders: bool = False
    wander_rooms: list[str] = Field(default_factory=list)
    steals_items: bool = False
    blocks_exit: str | None = None
    combat_messages: dict[str, str] = Field(default_factory=dict)


class NPC(BaseModel):
    """A non-player character."""
    id: str
    name: str
    aliases: list[str] = Field(default_factory=list)
    description: str = ""
    location: str | None = None
    attitude: NPCAttitude = NPCAttitude.NEUTRAL
    health: int = 10
    max_health: int = 10
    damage: int = 1
    behavior: NPCBehavior = Field(default_factory=NPCBehavior)
    death_message: str = ""
    death_flag: str | None = None
    inventory: list[str] = Field(default_factory=list)
