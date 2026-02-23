"""Tests for the action system."""

from __future__ import annotations

from engine.actions.builtin_actions import registry
from engine.models.command import ParsedCommand
from engine.models.enums import ObjectProperty


class TestLook:
    def test_look_at_room(self, state, world):
        handler = registry.get_handler("look")
        cmd = ParsedCommand(verb="look")
        result = handler(cmd, state, world)
        assert "Start Room" in result.message
        assert result.success

    def test_look_shows_objects(self, state, world):
        handler = registry.get_handler("look")
        cmd = ParsedCommand(verb="look")
        result = handler(cmd, state, world)
        assert "brass key" in result.message


class TestGo:
    def test_go_north(self, state, world):
        handler = registry.get_handler("go")
        cmd = ParsedCommand(verb="go", direction="north")
        result = handler(cmd, state, world)
        assert state.current_room == "north_room"
        assert result.success

    def test_go_invalid_direction(self, state, world):
        handler = registry.get_handler("go")
        cmd = ParsedCommand(verb="go", direction="west")
        result = handler(cmd, state, world)
        assert "can't go" in result.message.lower()
        assert not result.success

    def test_go_blocked_exit(self, state, world):
        state.current_room = "east_room"
        handler = registry.get_handler("go")
        cmd = ParsedCommand(verb="go", direction="north")
        result = handler(cmd, state, world)
        assert "locked" in result.message.lower()
        assert not result.success


class TestTake:
    def test_take_object(self, state, world):
        handler = registry.get_handler("take")
        cmd = ParsedCommand(verb="take", direct_object="key")
        result = handler(cmd, state, world)
        assert "key" in state.inventory
        assert result.success

    def test_take_already_held(self, state, world):
        state.inventory.append("key")
        handler = registry.get_handler("take")
        cmd = ParsedCommand(verb="take", direct_object="key")
        result = handler(cmd, state, world)
        assert "already" in result.message.lower()
        assert not result.success

    def test_take_fixed_object(self, state, world):
        handler = registry.get_handler("take")
        cmd = ParsedCommand(verb="take", direct_object="trophy_case")
        result = handler(cmd, state, world)
        assert "can't" in result.message.lower()
        assert not result.success


class TestDrop:
    def test_drop_object(self, state, world):
        state.inventory.append("key")
        handler = registry.get_handler("drop")
        cmd = ParsedCommand(verb="drop", direct_object="key")
        result = handler(cmd, state, world)
        assert "key" not in state.inventory
        assert state.get_object_location("key") == "start_room"
        assert result.success

    def test_drop_not_held(self, state, world):
        handler = registry.get_handler("drop")
        cmd = ParsedCommand(verb="drop", direct_object="key")
        result = handler(cmd, state, world)
        assert "not carrying" in result.message.lower()
        assert not result.success


class TestInventory:
    def test_empty_inventory(self, state, world):
        handler = registry.get_handler("inventory")
        cmd = ParsedCommand(verb="inventory")
        result = handler(cmd, state, world)
        assert "empty" in result.message.lower()

    def test_inventory_with_items(self, state, world):
        state.inventory.append("key")
        handler = registry.get_handler("inventory")
        cmd = ParsedCommand(verb="inventory")
        result = handler(cmd, state, world)
        assert "brass key" in result.message


class TestOpen:
    def test_open_container(self, state, world):
        handler = registry.get_handler("open")
        cmd = ParsedCommand(verb="open", direct_object="box")
        result = handler(cmd, state, world)
        assert state.has_object_property("box", ObjectProperty.OPEN)
        assert result.success

    def test_open_already_open(self, state, world):
        state.add_object_property("box", ObjectProperty.OPEN)
        handler = registry.get_handler("open")
        cmd = ParsedCommand(verb="open", direct_object="box")
        result = handler(cmd, state, world)
        assert "already open" in result.message.lower()


class TestExamine:
    def test_examine_object(self, state, world):
        handler = registry.get_handler("examine")
        cmd = ParsedCommand(verb="examine", direct_object="key")
        result = handler(cmd, state, world)
        assert "brass key" in result.message

    def test_examine_open_container(self, state, world):
        state.add_object_property("box", ObjectProperty.OPEN)
        handler = registry.get_handler("examine")
        cmd = ParsedCommand(verb="examine", direct_object="box")
        result = handler(cmd, state, world)
        assert "gold coin" in result.message


class TestPut:
    def test_put_in_container(self, state, world):
        state.inventory.append("key")
        state.add_object_property("box", ObjectProperty.OPEN)
        handler = registry.get_handler("put")
        cmd = ParsedCommand(verb="put", direct_object="key", indirect_object="box", preposition="in")
        result = handler(cmd, state, world)
        assert "key" not in state.inventory
        assert result.success

    def test_put_in_closed_container(self, state, world):
        state.inventory.append("key")
        handler = registry.get_handler("put")
        cmd = ParsedCommand(verb="put", direct_object="key", indirect_object="box", preposition="in")
        result = handler(cmd, state, world)
        assert "closed" in result.message.lower()
        assert not result.success


class TestTurnOn:
    def test_turn_on_lamp(self, state, world):
        state.inventory.append("lamp")
        handler = registry.get_handler("turn_on")
        cmd = ParsedCommand(verb="turn_on", direct_object="lamp")
        result = handler(cmd, state, world)
        assert state.has_object_property("lamp", ObjectProperty.LIT)
        assert result.success


class TestRead:
    def test_read_book(self, state, world):
        state.current_room = "east_room"
        state.inventory.append("book")
        handler = registry.get_handler("read")
        cmd = ParsedCommand(verb="read", direct_object="book")
        result = handler(cmd, state, world)
        assert "treasure" in result.message.lower()


class TestEat:
    def test_eat_apple(self, state, world):
        state.inventory.append("apple")
        handler = registry.get_handler("eat")
        cmd = ParsedCommand(verb="eat", direct_object="apple")
        result = handler(cmd, state, world)
        assert "apple" not in state.inventory
        assert result.success

    def test_eat_non_edible(self, state, world):
        state.inventory.append("key")
        handler = registry.get_handler("eat")
        cmd = ParsedCommand(verb="eat", direct_object="key")
        result = handler(cmd, state, world)
        assert "can't eat" in result.message.lower() or "not something" in result.message.lower()


class TestScore:
    def test_score_display(self, state, world):
        state.score = 5
        handler = registry.get_handler("score")
        cmd = ParsedCommand(verb="score")
        result = handler(cmd, state, world)
        assert "5" in result.message
        assert "Adventurer" in result.message


class TestAttack:
    def test_attack_npc(self, state, world):
        state.current_room = "east_room"
        state.inventory.append("sword")
        handler = registry.get_handler("attack")
        cmd = ParsedCommand(verb="attack", direct_object="guard")
        result = handler(cmd, state, world)
        assert result.success
        # With 5 damage sword vs 5 health guard, should be dead
        assert not state.npc_states["guard"].alive
        assert "guard_dead" in state.flags
