"""Build context-aware prompts for the LLM parser."""

from __future__ import annotations

from engine.parser.parser_interface import ParserContext

# Few-shot examples covering standard input, voice-like input, directions,
# multi-object commands, and pronoun resolution.
FEW_SHOT_EXAMPLES = [
    # Standard input
    {
        "input": "take the lamp",
        "output": '{"verb": "take", "direct_object": "brass lantern"}',
    },
    # Voice-like input with filler words
    {
        "input": "uh pick up that shiny thing",
        "output": '{"verb": "take", "direct_object": "brass lantern"}',
    },
    # Directional movement
    {
        "input": "go north",
        "output": '{"verb": "go", "direction": "north"}',
    },
    # Bare direction (voice)
    {
        "input": "i wanna go like west or something",
        "output": '{"verb": "go", "direction": "west"}',
    },
    # Multi-object with preposition
    {
        "input": "put the key in the box",
        "output": '{"verb": "put", "direct_object": "brass key", "indirect_object": "wooden box", "preposition": "in"}',
    },
    # Examine / look at
    {
        "input": "whats that leaflet say",
        "output": '{"verb": "read", "direct_object": "leaflet"}',
    },
    # Voice fragment with filler
    {
        "input": "um yeah open the uh mailbox",
        "output": '{"verb": "open", "direct_object": "small mailbox"}',
    },
    # Attack with instrument
    {
        "input": "hit the troll with my sword",
        "output": '{"verb": "attack", "direct_object": "troll", "indirect_object": "elvish sword", "preposition": "with"}',
    },
]


class PromptBuilder:
    """Builds prompts for the LLM parser with game context."""

    def build_system_prompt(self, context: ParserContext) -> str:
        verb_list = ", ".join(context.valid_verbs) if context.valid_verbs else "look, take, drop, go"

        lines = [
            "You are a text adventure game parser. Convert natural language input into a JSON command.",
            "",
            "Output JSON with these fields (omit null fields):",
            '  verb: string (REQUIRED) - one of: ' + verb_list,
            '  direct_object: string - the target object name exactly as listed below',
            '  indirect_object: string - secondary object (e.g., key for unlock, weapon for attack)',
            '  preposition: string - connecting word (in, on, with, at, to, from)',
            '  direction: string - for movement: north, south, east, west, up, down, northeast, northwest, southeast, southwest',
            "",
            "Rules:",
            "- Map the player intent to the closest verb from the valid verbs list",
            "- Resolve object references to the exact object names from context (visible objects or inventory)",
            "- For directional movement, use verb 'go' with the direction field",
            "- Ignore filler words (uh, um, like, yeah, so, well, hmm, ok)",
            "- Ignore false starts and repeated words",
            "- Handle voice transcription artifacts: missing punctuation, run-on sentences, homophones",
            "- Strip articles (the, a, an) and possessives (my, the) before matching objects",
            "- If the input is ambiguous, make your best guess from context",
            "- Never invent objects or verbs not in the context",
            "",
            "Examples:",
        ]

        for ex in FEW_SHOT_EXAMPLES:
            lines.append(f'  Input: "{ex["input"]}"')
            lines.append(f'  Output: {ex["output"]}')
            lines.append("")

        return "\n".join(lines)

    def build_user_prompt(self, input_text: str, context: ParserContext) -> str:
        parts = [f'Player input: "{input_text}"', "", "Context:"]

        if context.visible_objects:
            obj_parts = []
            for name in context.visible_objects:
                aliases = context.object_aliases.get(name)
                if aliases:
                    obj_parts.append(f"{name} (also: {', '.join(aliases)})")
                else:
                    obj_parts.append(name)
            parts.append(f"Visible objects: {'; '.join(obj_parts)}")

        if context.inventory:
            inv_parts = []
            for name in context.inventory:
                aliases = context.object_aliases.get(name)
                if aliases:
                    inv_parts.append(f"{name} (also: {', '.join(aliases)})")
                else:
                    inv_parts.append(name)
            parts.append(f"Inventory: {'; '.join(inv_parts)}")

        if context.exits:
            parts.append(f"Exits: {', '.join(context.exits)}")
        if context.npc_names:
            parts.append(f"NPCs present: {', '.join(context.npc_names)}")

        parts.append("")
        parts.append("Output:")
        return "\n".join(parts)
