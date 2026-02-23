"""Tests for the World query layer."""

from __future__ import annotations


class TestWorld:
    def test_get_room(self, world):
        room = world.get_room("start_room")
        assert room is not None
        assert room.name == "Start Room"

    def test_get_room_nonexistent(self, world):
        assert world.get_room("nowhere") is None

    def test_get_object(self, world):
        obj = world.get_object("key")
        assert obj is not None
        assert obj.name == "brass key"

    def test_resolve_object_name(self, world):
        ids = world.resolve_object_name("brass key")
        assert "key" in ids

    def test_resolve_object_alias(self, world):
        ids = world.resolve_object_name("key")
        assert "key" in ids

    def test_resolve_verb_name(self, world):
        verb_id = world.resolve_verb_name("take")
        assert verb_id == "take"

    def test_resolve_verb_alias(self, world):
        verb_id = world.resolve_verb_name("get")
        assert verb_id == "take"

    def test_get_npc(self, world):
        npc = world.get_npc("guard")
        assert npc is not None
        assert npc.name == "guard"

    def test_resolve_npc_name(self, world):
        ids = world.resolve_npc_name("guard")
        assert "guard" in ids

    def test_all_rooms(self, world):
        rooms = world.all_rooms()
        assert len(rooms) == 3

    def test_config(self, world):
        assert world.config.title == "Tiny World"
        assert world.config.starting_room == "start_room"
