"""Tests for Pydantic data models."""

from __future__ import annotations

import json

from engine.models import (
    Condition,
    ConditionType,
    Direction,
    Effect,
    EffectType,
    Event,
    Exit,
    GameConfig,
    GameObject,
    NPC,
    ObjectDescription,
    ObjectProperty,
    ParsedCommand,
    Room,
    TriggerType,
    VerbDefinition,
)


class TestEnums:
    def test_direction_values(self):
        assert Direction.NORTH == "north"
        assert Direction.UP == "up"

    def test_object_property_values(self):
        assert ObjectProperty.TAKEABLE == "takeable"
        assert ObjectProperty.LIGHT_SOURCE == "light_source"


class TestRoom:
    def test_create_room(self):
        room = Room(
            id="test", name="Test Room", description="A test room."
        )
        assert room.id == "test"
        assert room.exits == []
        assert room.is_dark is False

    def test_room_with_exits(self):
        room = Room(
            id="test",
            name="Test",
            description="Test",
            exits=[Exit(direction=Direction.NORTH, target_room="other")],
        )
        assert len(room.exits) == 1
        assert room.exits[0].target_room == "other"

    def test_room_json_roundtrip(self):
        room = Room(
            id="test", name="Test", description="Test", is_dark=True
        )
        data = json.loads(room.model_dump_json())
        room2 = Room(**data)
        assert room2.id == room.id
        assert room2.is_dark is True


class TestGameObject:
    def test_create_object(self):
        obj = GameObject(
            id="lamp",
            name="brass lantern",
            properties=[ObjectProperty.TAKEABLE, ObjectProperty.LIGHT_SOURCE],
        )
        assert obj.id == "lamp"
        assert ObjectProperty.TAKEABLE in obj.properties
        assert obj.light_fuel == -1  # infinite

    def test_object_json_roundtrip(self):
        obj = GameObject(
            id="key",
            name="brass key",
            aliases=["key"],
            location="room1",
            properties=[ObjectProperty.TAKEABLE],
        )
        data = json.loads(obj.model_dump_json())
        obj2 = GameObject(**data)
        assert obj2.aliases == ["key"]
        assert obj2.location == "room1"


class TestParsedCommand:
    def test_simple_command(self):
        cmd = ParsedCommand(verb="take", direct_object="lamp")
        assert cmd.verb == "take"
        assert cmd.indirect_object is None

    def test_full_command(self):
        cmd = ParsedCommand(
            verb="put",
            direct_object="coin",
            indirect_object="case",
            preposition="in",
            raw_input="put coin in case",
        )
        assert cmd.preposition == "in"

    def test_command_json_schema(self):
        schema = ParsedCommand.model_json_schema()
        assert "properties" in schema
        assert "verb" in schema["properties"]

    def test_direction_command(self):
        cmd = ParsedCommand(verb="go", direction="north")
        assert cmd.direction == "north"


class TestGameConfig:
    def test_config_defaults(self):
        config = GameConfig(starting_room="start")
        assert config.title == "Untitled Adventure"
        assert config.max_inventory_size == 100

    def test_config_ranks(self):
        config = GameConfig(
            starting_room="start",
            ranks={0: "Beginner", 100: "Expert"},
        )
        assert config.ranks[0] == "Beginner"


class TestEvent:
    def test_create_event(self):
        event = Event(
            id="test_event",
            trigger=TriggerType.AFTER_ACTION,
            conditions=[
                Condition(type=ConditionType.FLAG_SET, target="door_open")
            ],
            effects=[
                Effect(type=EffectType.PRINT_MESSAGE, value="The door opens!")
            ],
            once=True,
        )
        assert event.once is True
        assert len(event.conditions) == 1
        assert len(event.effects) == 1


class TestNPC:
    def test_create_npc(self):
        npc = NPC(id="troll", name="troll", health=10, damage=3)
        assert npc.health == 10
        assert npc.behavior.wanders is False
