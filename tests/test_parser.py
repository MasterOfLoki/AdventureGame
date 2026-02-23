"""Tests for the fallback parser."""

from __future__ import annotations

from engine.parser.fallback_parser import FallbackParser
from engine.parser.parser_interface import ParserContext


class TestFallbackParser:
    def setup_method(self):
        self.parser = FallbackParser()
        self.context = ParserContext(
            visible_objects=["brass key", "wooden box", "lamp"],
            inventory=["sword"],
            exits=["north", "east"],
            valid_verbs=["take", "drop", "look", "go"],
        )

    def test_bare_direction(self):
        cmd = self.parser.parse("north", self.context)
        assert cmd.verb == "go"
        assert cmd.direction == "north"

    def test_direction_abbreviation(self):
        cmd = self.parser.parse("n", self.context)
        assert cmd.verb == "go"
        assert cmd.direction == "north"

    def test_go_direction(self):
        cmd = self.parser.parse("go east", self.context)
        assert cmd.verb == "go"
        assert cmd.direction == "east"

    def test_simple_verb(self):
        cmd = self.parser.parse("look", self.context)
        assert cmd.verb == "look"

    def test_verb_object(self):
        cmd = self.parser.parse("take lamp", self.context)
        assert cmd.verb == "take"
        assert cmd.direct_object == "lamp"

    def test_verb_alias(self):
        cmd = self.parser.parse("get lamp", self.context)
        assert cmd.verb == "take"
        assert cmd.direct_object == "lamp"

    def test_pick_up(self):
        cmd = self.parser.parse("pick up lamp", self.context)
        assert cmd.verb == "take"
        assert cmd.direct_object == "lamp"

    def test_verb_with_preposition(self):
        cmd = self.parser.parse("put sword in box", self.context)
        assert cmd.verb == "put"
        assert cmd.direct_object == "sword"
        assert cmd.preposition == "in"

    def test_turn_on(self):
        cmd = self.parser.parse("turn on lamp", self.context)
        assert cmd.verb == "turn_on"
        assert cmd.direct_object == "lamp"

    def test_turn_off(self):
        cmd = self.parser.parse("turn off lamp", self.context)
        assert cmd.verb == "turn_off"
        assert cmd.direct_object == "lamp"

    def test_look_at(self):
        cmd = self.parser.parse("look at lamp", self.context)
        assert cmd.verb == "examine"
        assert cmd.direct_object == "lamp"

    def test_inventory_shortcut(self):
        cmd = self.parser.parse("i", self.context)
        assert cmd.verb == "inventory"

    def test_examine_shortcut(self):
        cmd = self.parser.parse("x lamp", self.context)
        assert cmd.verb == "examine"
        assert cmd.direct_object == "lamp"

    def test_article_removal(self):
        cmd = self.parser.parse("take the lamp", self.context)
        assert cmd.verb == "take"
        assert cmd.direct_object == "lamp"

    def test_empty_input(self):
        cmd = self.parser.parse("", self.context)
        assert cmd.verb == "look"

    def test_raw_input_preserved(self):
        cmd = self.parser.parse("pick up the lamp", self.context)
        assert cmd.raw_input == "pick up the lamp"

    def test_wait_shortcut(self):
        cmd = self.parser.parse("z", self.context)
        assert cmd.verb == "wait"

    def test_take_from(self):
        cmd = self.parser.parse("take coin from box", self.context)
        assert cmd.verb == "take_from"
        assert cmd.direct_object == "coin"
        assert cmd.preposition == "from"
