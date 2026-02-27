"""Integration tests for LLM parser with a real model.

Skipped by default. To run:
    ADVENTURE_TEST_MODEL=models/qwen2.5-3b-instruct-q4_k_m.gguf pytest tests/test_llm_integration.py -v
"""

from __future__ import annotations

import os

import pytest

from engine.parser.parser_interface import ParserContext

MODEL_PATH = os.environ.get("ADVENTURE_TEST_MODEL", "")

pytestmark = pytest.mark.skipif(
    not MODEL_PATH or not os.path.exists(MODEL_PATH),
    reason="Set ADVENTURE_TEST_MODEL to a valid .gguf path to run integration tests",
)


@pytest.fixture(scope="module")
def parser():
    """Create an LLMParser with the real model (shared across tests)."""
    from engine.parser.llm_parser import LLMParser
    return LLMParser(model_path=MODEL_PATH)


@pytest.fixture
def context():
    return ParserContext(
        visible_objects=["brass lantern", "small mailbox", "leaflet", "wooden door"],
        inventory=["elvish sword", "brass key"],
        exits=["north", "south", "east", "west"],
        valid_verbs=[
            "look", "examine", "take", "drop", "go", "open", "close",
            "read", "attack", "put", "turn_on", "turn_off", "unlock",
            "inventory", "wait",
        ],
        npc_names=["troll"],
        object_aliases={
            "brass lantern": ["lantern", "lamp"],
            "small mailbox": ["mailbox"],
            "elvish sword": ["sword"],
            "brass key": ["key"],
        },
    )


class TestStandardCommands:
    def test_take_object(self, parser, context):
        result = parser.parse("take the lantern", context)
        assert result.verb == "take"
        assert "lantern" in (result.direct_object or "").lower() or "brass lantern" == result.direct_object

    def test_go_direction(self, parser, context):
        result = parser.parse("go north", context)
        assert result.verb == "go"
        assert result.direction == "north"

    def test_open_object(self, parser, context):
        result = parser.parse("open the mailbox", context)
        assert result.verb == "open"
        assert result.direct_object is not None

    def test_examine_object(self, parser, context):
        result = parser.parse("look at the leaflet", context)
        assert result.verb in ("examine", "look")

    def test_attack_with_weapon(self, parser, context):
        result = parser.parse("attack troll with sword", context)
        assert result.verb == "attack"
        assert result.direct_object is not None

    def test_read(self, parser, context):
        result = parser.parse("read the leaflet", context)
        assert result.verb == "read"


class TestVoiceLikeInput:
    """Test messy, unpunctuated, filler-laden input like voice transcription."""

    def test_filler_words(self, parser, context):
        result = parser.parse("uh pick up that shiny lamp thing", context)
        assert result.verb == "take"

    def test_run_on_direction(self, parser, context):
        result = parser.parse("i wanna go north", context)
        assert result.verb == "go"
        assert result.direction == "north"

    def test_informal_examine(self, parser, context):
        result = parser.parse("whats in the mailbox", context)
        assert result.verb in ("look", "examine", "open")

    def test_hesitation(self, parser, context):
        result = parser.parse("um yeah open the uh mailbox", context)
        assert result.verb == "open"

    def test_grab_synonym(self, parser, context):
        result = parser.parse("grab the lantern", context)
        assert result.verb == "take"

    def test_fragment(self, parser, context):
        result = parser.parse("go like west", context)
        assert result.verb == "go"
        assert result.direction == "west"
