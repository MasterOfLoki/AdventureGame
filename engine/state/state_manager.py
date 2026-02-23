"""Save and load game state to/from JSON files."""

from __future__ import annotations

import json
from pathlib import Path

from engine.state.game_state import GameState


class StateManager:
    """Manages saving and loading game state."""

    def __init__(self, save_dir: str | Path = "saves"):
        self.save_dir = Path(save_dir)

    def save(self, state: GameState, slot: str = "quicksave") -> Path:
        self.save_dir.mkdir(parents=True, exist_ok=True)
        save_path = self.save_dir / f"{slot}.json"
        data = state.model_dump(mode="json")
        # Convert sets to sorted lists for JSON
        data["flags"] = sorted(data["flags"])
        data["visited_rooms"] = sorted(data["visited_rooms"])
        data["fired_events"] = sorted(data["fired_events"])
        for obj_state in data.get("object_states", {}).values():
            obj_state["properties"] = sorted(obj_state["properties"])
        with open(save_path, "w") as f:
            json.dump(data, f, indent=2)
        return save_path

    def load(self, slot: str = "quicksave") -> GameState:
        save_path = self.save_dir / f"{slot}.json"
        if not save_path.exists():
            raise FileNotFoundError(f"No save found: {save_path}")
        with open(save_path) as f:
            data = json.load(f)
        return GameState(**data)

    def list_saves(self) -> list[str]:
        if not self.save_dir.exists():
            return []
        return [p.stem for p in sorted(self.save_dir.glob("*.json"))]
