"""Tests for darkness and light mechanics."""

from __future__ import annotations

from engine.models.enums import ObjectProperty
from engine.world.darkness import DarknessSystem


class TestDarkness:
    def test_lit_room_not_dark(self, state, world):
        ds = DarknessSystem()
        assert not ds.is_dark(state, world)  # start_room is not dark

    def test_dark_room_without_light(self, state, world):
        ds = DarknessSystem()
        state.current_room = "north_room"
        assert ds.is_dark(state, world)

    def test_dark_room_with_light(self, state, world):
        ds = DarknessSystem()
        state.current_room = "north_room"
        state.inventory.append("lamp")
        state.add_object_property("lamp", ObjectProperty.LIT)
        assert not ds.is_dark(state, world)

    def test_grue_warning(self, state, world):
        ds = DarknessSystem()
        state.current_room = "north_room"
        msg = ds.tick(state, world)
        assert "grue" in msg.lower()
        assert state.player_alive  # Warning only

    def test_grue_kills(self, state, world):
        ds = DarknessSystem()
        state.current_room = "north_room"
        ds.tick(state, world)  # Warning
        msg = ds.tick(state, world)  # Death
        assert not state.player_alive
        assert "died" in msg.lower()

    def test_light_resets_dark_turns(self, state, world):
        ds = DarknessSystem()
        state.current_room = "north_room"
        ds.tick(state, world)  # dark_turns = 1
        # Turn on light
        state.inventory.append("lamp")
        state.add_object_property("lamp", ObjectProperty.LIT)
        msg = ds.tick(state, world)
        assert msg is None
        assert state.dark_turns == 0

    def test_light_fuel_depletion(self, state, world):
        ds = DarknessSystem()
        state.inventory.append("lamp")
        state.add_object_property("lamp", ObjectProperty.LIT)
        state.counters["fuel_lamp"] = 1
        msg = ds.tick_light_sources(state, world)
        assert msg is not None
        assert "run out" in msg.lower()
        assert not state.has_object_property("lamp", ObjectProperty.LIT)
