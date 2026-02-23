"""Tests for game state management."""

from __future__ import annotations

import json
import tempfile
from pathlib import Path

from engine.models.enums import ObjectProperty
from engine.state.game_state import GameState, ObjectState
from engine.state.state_manager import StateManager


class TestGameState:
    def test_initial_state(self):
        state = GameState(current_room="start")
        assert state.current_room == "start"
        assert state.inventory == []
        assert state.score == 0
        assert state.turns == 0
        assert state.player_alive is True

    def test_object_location(self):
        state = GameState(current_room="room1")
        state.set_object_location("key", "room1")
        assert state.get_object_location("key") == "room1"
        assert "key" in state.objects_in_room("room1")

    def test_object_properties(self):
        state = GameState(current_room="room1")
        state.object_states["lamp"] = ObjectState(
            location="room1", properties={ObjectProperty.LIGHT_SOURCE}
        )
        assert state.has_object_property("lamp", ObjectProperty.LIGHT_SOURCE)
        state.add_object_property("lamp", ObjectProperty.LIT)
        assert state.has_object_property("lamp", ObjectProperty.LIT)
        state.remove_object_property("lamp", ObjectProperty.LIT)
        assert not state.has_object_property("lamp", ObjectProperty.LIT)

    def test_inventory(self):
        state = GameState(current_room="room1")
        state.inventory.append("key")
        assert state.player_has("key")
        assert not state.player_has("sword")

    def test_flags(self):
        state = GameState(current_room="room1")
        state.flags.add("door_open")
        assert "door_open" in state.flags

    def test_objects_in_container(self):
        state = GameState(current_room="room1")
        state.object_states["box"] = ObjectState(location="room1")
        state.object_states["coin"] = ObjectState(parent_object="box")
        assert "coin" in state.objects_in_container("box")


class TestStateManager:
    def test_save_and_load(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            manager = StateManager(tmpdir)
            state = GameState(current_room="test_room")
            state.score = 42
            state.flags.add("test_flag")
            state.inventory.append("key")

            manager.save(state, "test")
            loaded = manager.load("test")

            assert loaded.current_room == "test_room"
            assert loaded.score == 42
            assert "test_flag" in loaded.flags
            assert "key" in loaded.inventory

    def test_load_nonexistent(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            manager = StateManager(tmpdir)
            import pytest
            with pytest.raises(FileNotFoundError):
                manager.load("nonexistent")

    def test_list_saves(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            manager = StateManager(tmpdir)
            state = GameState(current_room="test")
            manager.save(state, "save1")
            manager.save(state, "save2")
            saves = manager.list_saves()
            assert "save1" in saves
            assert "save2" in saves
