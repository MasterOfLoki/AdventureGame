"""LLM-powered parser using llama-cpp-python with structured output."""

from __future__ import annotations

import json

from engine.models.command import ParsedCommand
from engine.parser.parser_interface import ParserContext, ParserInterface
from engine.parser.prompt_builder import PromptBuilder

try:
    from llama_cpp import Llama
except ImportError:
    Llama = None


class LLMParser(ParserInterface):
    """Parser that uses a local LLM for natural language understanding."""

    def __init__(self, model_path: str, n_ctx: int = 2048, n_gpu_layers: int = -1):
        if Llama is None:
            raise ImportError(
                "llama-cpp-python is required for LLM parsing. "
                "Install with: pip install llama-cpp-python"
            )
        self.llm = Llama(
            model_path=model_path,
            n_ctx=n_ctx,
            n_gpu_layers=n_gpu_layers,
            verbose=False,
        )
        self.prompt_builder = PromptBuilder()
        self._schema = ParsedCommand.model_json_schema()

    def parse(self, input_text: str, context: ParserContext) -> ParsedCommand:
        system_prompt = self.prompt_builder.build_system_prompt()
        user_prompt = self.prompt_builder.build_user_prompt(input_text, context)

        response = self.llm.create_chat_completion(
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            response_format={
                "type": "json_object",
                "schema": self._schema,
            },
            temperature=0.1,
            max_tokens=256,
        )

        content = response["choices"][0]["message"]["content"]
        data = json.loads(content)
        data["raw_input"] = input_text
        return ParsedCommand(**data)
