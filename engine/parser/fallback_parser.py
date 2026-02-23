"""Regex/keyword parser that works without an LLM."""

from __future__ import annotations

import re

from engine.models.command import ParsedCommand
from engine.models.enums import DIRECTION_ABBREVIATIONS, Direction
from engine.parser.parser_interface import ParserContext, ParserInterface

# Prepositions that split direct/indirect objects
PREPOSITIONS = {"in", "on", "with", "at", "to", "from", "into", "onto", "under", "behind", "through"}

# Verb aliases mapping common words to canonical verb IDs
VERB_ALIASES: dict[str, str] = {
    "l": "look",
    "look": "look",
    "examine": "examine",
    "x": "examine",
    "inspect": "examine",
    "get": "take",
    "take": "take",
    "grab": "take",
    "pick": "take",
    "drop": "drop",
    "throw": "drop",
    "i": "inventory",
    "inv": "inventory",
    "inventory": "inventory",
    "go": "go",
    "walk": "go",
    "run": "go",
    "move": "move",
    "push": "move",
    "pull": "move",
    "open": "open",
    "close": "close",
    "shut": "close",
    "turn": "turn_on",
    "light": "turn_on",
    "extinguish": "turn_off",
    "put": "put",
    "place": "put",
    "insert": "put",
    "unlock": "unlock",
    "lock": "lock",
    "read": "read",
    "eat": "eat",
    "drink": "eat",
    "attack": "attack",
    "kill": "attack",
    "hit": "attack",
    "fight": "attack",
    "strike": "attack",
    "wait": "wait",
    "z": "wait",
    "score": "score",
    "quit": "quit",
    "q": "quit",
    "save": "save",
    "restore": "restore",
    "load": "restore",
}

# Direction names (full) to Direction enum
DIRECTION_NAMES: dict[str, str] = {
    d.value: d.value for d in Direction
}
DIRECTION_NAMES.update({
    abbr: d.value for abbr, d in DIRECTION_ABBREVIATIONS.items()
})


class FallbackParser(ParserInterface):
    """Simple keyword/regex parser for use without an LLM."""

    def parse(self, input_text: str, context: ParserContext) -> ParsedCommand:
        raw = input_text.strip()
        text = raw.lower()

        if not text:
            return ParsedCommand(verb="look", raw_input=raw)

        # Check for bare direction (n, south, etc.)
        if text in DIRECTION_NAMES:
            return ParsedCommand(
                verb="go",
                direction=DIRECTION_NAMES[text],
                raw_input=raw,
            )

        words = text.split()
        if not words:
            return ParsedCommand(verb="look", raw_input=raw)

        verb_word = words[0]
        rest = words[1:]

        # Handle "pick up X" -> take X
        if verb_word == "pick" and rest and rest[0] == "up":
            return ParsedCommand(
                verb="take",
                direct_object=self._match_object(" ".join(rest[1:]), context) if len(rest) > 1 else None,
                raw_input=raw,
            )

        # Handle "turn on/off X"
        if verb_word == "turn" and rest:
            if rest[0] == "on":
                return ParsedCommand(
                    verb="turn_on",
                    direct_object=self._match_object(" ".join(rest[1:]), context) if len(rest) > 1 else None,
                    raw_input=raw,
                )
            if rest[0] == "off":
                return ParsedCommand(
                    verb="turn_off",
                    direct_object=self._match_object(" ".join(rest[1:]), context) if len(rest) > 1 else None,
                    raw_input=raw,
                )

        # Handle "look at X" -> examine
        if verb_word == "look" and rest and rest[0] == "at":
            return ParsedCommand(
                verb="examine",
                direct_object=self._match_object(" ".join(rest[1:]), context) if len(rest) > 1 else None,
                raw_input=raw,
            )

        # Resolve verb
        verb_id = VERB_ALIASES.get(verb_word, verb_word)

        # If verb is "go" and next word is direction
        if verb_id == "go" and rest and rest[0] in DIRECTION_NAMES:
            return ParsedCommand(
                verb="go",
                direction=DIRECTION_NAMES[rest[0]],
                raw_input=raw,
            )

        if not rest:
            return ParsedCommand(verb=verb_id, raw_input=raw)

        # Split on preposition
        preposition = None
        direct_parts = []
        indirect_parts = []
        found_prep = False
        for word in rest:
            if word in PREPOSITIONS and not found_prep:
                preposition = word
                found_prep = True
            elif found_prep:
                indirect_parts.append(word)
            else:
                direct_parts.append(word)

        direct_text = " ".join(direct_parts) if direct_parts else None
        indirect_text = " ".join(indirect_parts) if indirect_parts else None

        # Handle "take X from Y" -> take_from
        if verb_id == "take" and preposition == "from" and indirect_text:
            return ParsedCommand(
                verb="take_from",
                direct_object=self._match_object(direct_text, context) if direct_text else None,
                indirect_object=self._match_object(indirect_text, context),
                preposition=preposition,
                raw_input=raw,
            )

        direct_object = self._match_object(direct_text, context) if direct_text else None
        indirect_object = self._match_object(indirect_text, context) if indirect_text else None

        return ParsedCommand(
            verb=verb_id,
            direct_object=direct_object,
            indirect_object=indirect_object,
            preposition=preposition,
            raw_input=raw,
        )

    def _match_object(self, text: str | None, context: ParserContext) -> str | None:
        """Try to match text against known objects. Returns object ID or original text."""
        if not text:
            return None

        text = text.strip()
        # Remove articles
        text = re.sub(r"^(the|a|an|some)\s+", "", text)

        if not text:
            return None

        # Check visible objects and inventory for matches
        all_objects = context.visible_objects + context.inventory
        for obj_name in all_objects:
            if text == obj_name.lower():
                return obj_name

        # Check NPC names
        for npc_name in context.npc_names:
            if text == npc_name.lower():
                return npc_name

        # Return the cleaned text for the resolver to handle
        return text
