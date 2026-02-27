"""Tests for the LLM parser using mocked Llama."""

from __future__ import annotations

import json
from unittest.mock import MagicMock, patch

import pytest

from engine.models.command import ParsedCommand
from engine.parser.parser_interface import ParserContext
from engine.parser.prompt_builder import PromptBuilder


@pytest.fixture
def context():
    return ParserContext(
        visible_objects=["brass lantern", "small mailbox", "leaflet"],
        inventory=["elvish sword"],
        exits=["north", "south", "west"],
        valid_verbs=["look", "take", "drop", "go", "open", "read", "attack", "put", "examine"],
        npc_names=["troll"],
        object_aliases={"brass lantern": ["lantern", "lamp"], "small mailbox": ["mailbox"]},
    )


def _make_llm_response(data: dict) -> dict:
    """Build a fake Llama chat completion response."""
    return {
        "choices": [
            {"message": {"content": json.dumps(data)}}
        ]
    }


def _make_bad_response(text: str) -> dict:
    """Build a fake response with invalid content."""
    return {
        "choices": [
            {"message": {"content": text}}
        ]
    }


class TestPromptBuilder:
    def test_system_prompt_contains_verbs(self, context):
        builder = PromptBuilder()
        prompt = builder.build_system_prompt(context)
        assert "look" in prompt
        assert "take" in prompt
        assert "attack" in prompt

    def test_system_prompt_contains_examples(self, context):
        builder = PromptBuilder()
        prompt = builder.build_system_prompt(context)
        assert "take the lamp" in prompt
        assert "uh pick up that shiny thing" in prompt
        assert "go north" in prompt

    def test_system_prompt_contains_voice_instructions(self, context):
        builder = PromptBuilder()
        prompt = builder.build_system_prompt(context)
        assert "filler" in prompt.lower()
        assert "voice" in prompt.lower()

    def test_user_prompt_contains_input(self, context):
        builder = PromptBuilder()
        prompt = builder.build_user_prompt("grab the lamp", context)
        assert "grab the lamp" in prompt

    def test_user_prompt_contains_objects(self, context):
        builder = PromptBuilder()
        prompt = builder.build_user_prompt("look", context)
        assert "brass lantern" in prompt
        assert "small mailbox" in prompt

    def test_user_prompt_contains_aliases(self, context):
        builder = PromptBuilder()
        prompt = builder.build_user_prompt("look", context)
        assert "lantern" in prompt
        assert "lamp" in prompt
        assert "also:" in prompt

    def test_user_prompt_contains_inventory_aliases(self, context):
        builder = PromptBuilder()
        prompt = builder.build_user_prompt("look", context)
        assert "elvish sword" in prompt

    def test_user_prompt_contains_exits(self, context):
        builder = PromptBuilder()
        prompt = builder.build_user_prompt("look", context)
        assert "north" in prompt
        assert "south" in prompt

    def test_user_prompt_contains_npcs(self, context):
        builder = PromptBuilder()
        prompt = builder.build_user_prompt("look", context)
        assert "troll" in prompt

    def test_user_prompt_ends_with_output_cue(self, context):
        builder = PromptBuilder()
        prompt = builder.build_user_prompt("look", context)
        assert prompt.strip().endswith("Output:")


class TestLLMParserMocked:
    """Test LLMParser with mocked Llama class."""

    def _make_parser(self, mock_llama_cls):
        """Create an LLMParser with a mocked Llama instance."""
        with patch.dict("sys.modules", {"llama_cpp": MagicMock()}):
            # We need to re-import to pick up the mock
            import importlib
            import engine.parser.llm_parser as llm_module
            importlib.reload(llm_module)

            mock_instance = MagicMock()
            mock_llama_cls.return_value = mock_instance

            # Patch Llama at module level
            llm_module.Llama = mock_llama_cls
            parser = llm_module.LLMParser.__new__(llm_module.LLMParser)
            parser.llm = mock_instance
            parser.prompt_builder = PromptBuilder()
            parser._schema = ParsedCommand.model_json_schema()
            from engine.parser.fallback_parser import FallbackParser
            parser._fallback = FallbackParser()

            return parser, mock_instance

    def test_successful_parse(self, context):
        mock_llama_cls = MagicMock()
        parser, mock_llm = self._make_parser(mock_llama_cls)

        mock_llm.create_chat_completion.return_value = _make_llm_response(
            {"verb": "take", "direct_object": "brass lantern"}
        )

        result = parser.parse("grab the lamp", context)
        assert result.verb == "take"
        assert result.direct_object == "brass lantern"
        assert result.raw_input == "grab the lamp"

    def test_successful_direction_parse(self, context):
        mock_llama_cls = MagicMock()
        parser, mock_llm = self._make_parser(mock_llama_cls)

        mock_llm.create_chat_completion.return_value = _make_llm_response(
            {"verb": "go", "direction": "north"}
        )

        result = parser.parse("i wanna go north", context)
        assert result.verb == "go"
        assert result.direction == "north"

    def test_retry_on_bad_json_then_succeed(self, context):
        mock_llama_cls = MagicMock()
        parser, mock_llm = self._make_parser(mock_llama_cls)

        # First call returns bad JSON, second succeeds
        mock_llm.create_chat_completion.side_effect = [
            _make_bad_response("not valid json {{{"),
            _make_llm_response({"verb": "look"}),
        ]

        result = parser.parse("look around", context)
        assert result.verb == "look"
        assert mock_llm.create_chat_completion.call_count == 2

    def test_fallback_on_total_failure(self, context):
        mock_llama_cls = MagicMock()
        parser, mock_llm = self._make_parser(mock_llama_cls)

        # Both calls return bad JSON
        mock_llm.create_chat_completion.side_effect = [
            _make_bad_response("garbage"),
            _make_bad_response("more garbage"),
        ]

        # Should fall back to FallbackParser — "take lamp" is understood by keyword parser
        result = parser.parse("take lamp", context)
        assert result.verb == "take"
        assert result.direct_object == "lamp"

    def test_fallback_on_exception(self, context):
        mock_llama_cls = MagicMock()
        parser, mock_llm = self._make_parser(mock_llama_cls)

        mock_llm.create_chat_completion.side_effect = RuntimeError("model crashed")

        result = parser.parse("look", context)
        assert result.verb == "look"

    def test_missing_verb_triggers_retry(self, context):
        mock_llama_cls = MagicMock()
        parser, mock_llm = self._make_parser(mock_llama_cls)

        mock_llm.create_chat_completion.side_effect = [
            _make_llm_response({"direct_object": "lamp"}),  # missing verb
            _make_llm_response({"verb": "take", "direct_object": "brass lantern"}),
        ]

        result = parser.parse("grab lamp", context)
        assert result.verb == "take"
        assert mock_llm.create_chat_completion.call_count == 2

    def test_preposition_parse(self, context):
        mock_llama_cls = MagicMock()
        parser, mock_llm = self._make_parser(mock_llama_cls)

        mock_llm.create_chat_completion.return_value = _make_llm_response(
            {
                "verb": "attack",
                "direct_object": "troll",
                "indirect_object": "elvish sword",
                "preposition": "with",
            }
        )

        result = parser.parse("hit the troll with my sword", context)
        assert result.verb == "attack"
        assert result.direct_object == "troll"
        assert result.indirect_object == "elvish sword"
        assert result.preposition == "with"
