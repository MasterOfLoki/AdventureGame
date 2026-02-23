"""Loads game data from a directory of JSON files into Pydantic models."""

from __future__ import annotations

import json
from pathlib import Path

from engine.models import (
    Event,
    GameConfig,
    GameObject,
    NPC,
    Room,
    VerbDefinition,
)


class GameData:
    """Container for all loaded game data."""

    def __init__(
        self,
        config: GameConfig,
        rooms: list[Room],
        objects: list[GameObject],
        npcs: list[NPC],
        verbs: list[VerbDefinition],
        events: list[Event],
    ):
        self.config = config
        self.rooms = rooms
        self.objects = objects
        self.npcs = npcs
        self.verbs = verbs
        self.events = events


class GameLoader:
    """Reads a game directory and produces validated GameData."""

    def __init__(self, game_dir: str | Path):
        self.game_dir = Path(game_dir)

    def load(self) -> GameData:
        config = self._load_config()
        rooms = self._load_items("rooms", Room)
        objects = self._load_items("objects", GameObject)
        npcs = self._load_items("npcs", NPC)
        verbs = self._load_items("verbs", VerbDefinition)
        events = self._load_items("events", Event)
        return GameData(
            config=config,
            rooms=rooms,
            objects=objects,
            npcs=npcs,
            verbs=verbs,
            events=events,
        )

    def _load_config(self) -> GameConfig:
        config_path = self.game_dir / "game.json"
        if not config_path.exists():
            raise FileNotFoundError(f"Game config not found: {config_path}")
        with open(config_path) as f:
            data = json.load(f)
        return GameConfig(**data)

    def _load_items(self, subdir: str, model_class: type):
        dir_path = self.game_dir / subdir
        items = []
        if not dir_path.exists():
            return items
        for file_path in sorted(dir_path.glob("*.json")):
            with open(file_path) as f:
                data = json.load(f)
            if isinstance(data, list):
                for item_data in data:
                    items.append(model_class(**item_data))
            else:
                items.append(model_class(**data))
        return items
