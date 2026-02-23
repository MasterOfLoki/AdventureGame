"""Room and exit models."""

from __future__ import annotations

from pydantic import BaseModel, Field

from engine.models.enums import Direction


class ExitCondition(BaseModel):
    """Condition that must be met for an exit to be usable."""
    flag: str | None = None
    object_property: str | None = None
    object_id: str | None = None
    message_if_blocked: str = "You can't go that way."


class Exit(BaseModel):
    """An exit from a room."""
    direction: Direction
    target_room: str
    condition: ExitCondition | None = None
    description: str | None = None
    hidden: bool = False


class Room(BaseModel):
    """A room/location in the game world."""
    id: str
    name: str
    description: str
    short_description: str | None = None
    exits: list[Exit] = Field(default_factory=list)
    is_dark: bool = False
    dark_description: str = "It is pitch black. You are likely to be eaten by a grue."
    first_visit_description: str | None = None
    properties: dict[str, str | int | bool] = Field(default_factory=dict)
