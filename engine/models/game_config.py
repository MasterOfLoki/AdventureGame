"""Game configuration model."""

from __future__ import annotations

from pydantic import BaseModel, Field


class GameConfig(BaseModel):
    """Top-level game configuration loaded from game.json."""
    title: str = "Untitled Adventure"
    author: str = "Unknown"
    version: str = "1.0"
    description: str = ""
    starting_room: str
    intro_text: str = ""
    max_score: int = 0
    max_inventory_size: int = 100
    ranks: dict[int, str] = Field(default_factory=dict)
    settings: dict[str, str | int | bool] = Field(default_factory=dict)
