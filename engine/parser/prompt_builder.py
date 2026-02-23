"""Build context-aware prompts for the LLM parser."""

from __future__ import annotations

from engine.parser.parser_interface import ParserContext


class PromptBuilder:
    """Builds prompts for the LLM parser with game context."""

    def build_system_prompt(self) -> str:
        return (
            "You are a text adventure game parser. Your job is to translate natural language "
            "input into structured commands. You must output valid JSON matching the schema.\n"
            "Rules:\n"
            "- Map the player's intent to the closest verb from the valid verbs list\n"
            "- Resolve object references to the exact object IDs from the visible objects or inventory\n"
            "- For directional movement, use verb 'go' with the direction field\n"
            "- If the input is unclear, make your best guess\n"
            "- Never invent objects or verbs not in the context"
        )

    def build_user_prompt(self, input_text: str, context: ParserContext) -> str:
        parts = [f'Player input: "{input_text}"', "", "Context:"]

        if context.visible_objects:
            parts.append(f"Visible objects: {', '.join(context.visible_objects)}")
        if context.inventory:
            parts.append(f"Inventory: {', '.join(context.inventory)}")
        if context.exits:
            parts.append(f"Exits: {', '.join(context.exits)}")
        if context.valid_verbs:
            parts.append(f"Valid verbs: {', '.join(context.valid_verbs)}")
        if context.npc_names:
            parts.append(f"NPCs present: {', '.join(context.npc_names)}")

        parts.append("")
        parts.append("Output the parsed command as JSON.")
        return "\n".join(parts)
