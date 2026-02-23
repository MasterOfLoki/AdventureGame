"""Tests for game data loader and validator."""

from __future__ import annotations

import pytest

from engine.loader import GameLoader, Validator


class TestGameLoader:
    def test_load_tiny_world(self, tiny_world_dir):
        loader = GameLoader(tiny_world_dir)
        data = loader.load()
        assert data.config.title == "Tiny World"
        assert data.config.starting_room == "start_room"
        assert len(data.rooms) == 3
        assert len(data.objects) >= 5
        assert len(data.verbs) >= 10

    def test_load_nonexistent_dir(self):
        loader = GameLoader("/nonexistent/path")
        with pytest.raises(FileNotFoundError):
            loader.load()

    def test_room_ids(self, game_data):
        room_ids = {r.id for r in game_data.rooms}
        assert "start_room" in room_ids
        assert "north_room" in room_ids
        assert "east_room" in room_ids


class TestValidator:
    def test_valid_data(self, game_data):
        validator = Validator()
        errors = validator.validate(game_data)
        assert len(errors) == 0

    def test_validates_exit_targets(self, game_data):
        # Corrupt an exit target
        game_data.rooms[0].exits[0].target_room = "nonexistent"
        validator = Validator()
        errors = validator.validate(game_data)
        assert len(errors) > 0
        assert "nonexistent" in errors[0].message
