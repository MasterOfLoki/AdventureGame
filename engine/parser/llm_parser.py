"""LLM-powered parser using llama-cpp-python with structured output."""

from __future__ import annotations

import json
import logging
import signal
import sys

from engine.models.command import ParsedCommand
from engine.parser.fallback_parser import FallbackParser
from engine.parser.parser_interface import ParserContext, ParserInterface
from engine.parser.prompt_builder import PromptBuilder

try:
    from llama_cpp import Llama
except ImportError:
    Llama = None

logger = logging.getLogger(__name__)

MAX_RETRIES = 2
TIMEOUT_SECONDS = 10


class LLMParseError(Exception):
    """Raised when the LLM fails to produce a valid parse."""
    pass


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
        self._fallback = FallbackParser()

    def parse(self, input_text: str, context: ParserContext) -> ParsedCommand:
        system_prompt = self.prompt_builder.build_system_prompt(context)
        user_prompt = self.prompt_builder.build_user_prompt(input_text, context)

        last_error: Exception | None = None
        for attempt in range(MAX_RETRIES):
            try:
                result = self._call_llm(system_prompt, user_prompt, input_text)
                return result
            except LLMParseError as e:
                last_error = e
                logger.warning("LLM parse attempt %d failed: %s", attempt + 1, e)

        # All retries exhausted — fall back to keyword parser
        logger.warning(
            "LLM parser failed after %d attempts, falling back to keyword parser: %s",
            MAX_RETRIES,
            last_error,
        )
        return self._fallback.parse(input_text, context)

    def _call_llm(
        self, system_prompt: str, user_prompt: str, raw_input: str
    ) -> ParsedCommand:
        """Make a single LLM call with timeout. Raises LLMParseError on failure."""
        # Set up timeout (Unix only; on Windows, skip timeout)
        use_alarm = hasattr(signal, "SIGALRM") and sys.platform != "win32"
        if use_alarm:
            old_handler = signal.signal(signal.SIGALRM, _timeout_handler)
            signal.alarm(TIMEOUT_SECONDS)

        try:
            response = self.llm.create_chat_completion(
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt},
                ],
                response_format={
                    "type": "json_object",
                    "schema": self._schema,
                },
                temperature=0.0,
                max_tokens=200,
            )
        except _LLMTimeoutError:
            raise LLMParseError("LLM inference timed out")
        except Exception as e:
            raise LLMParseError(f"LLM inference failed: {e}") from e
        finally:
            if use_alarm:
                signal.alarm(0)
                signal.signal(signal.SIGALRM, old_handler)

        # Parse response
        try:
            content = response["choices"][0]["message"]["content"]
        except (KeyError, IndexError, TypeError) as e:
            raise LLMParseError(f"Unexpected LLM response structure: {e}") from e

        try:
            data = json.loads(content)
        except json.JSONDecodeError as e:
            raise LLMParseError(f"LLM returned invalid JSON: {e}") from e

        # Validate required field
        if "verb" not in data:
            raise LLMParseError("LLM response missing required 'verb' field")

        data["raw_input"] = raw_input
        try:
            return ParsedCommand(**data)
        except Exception as e:
            raise LLMParseError(f"Failed to construct ParsedCommand: {e}") from e


class _LLMTimeoutError(Exception):
    """Internal exception for LLM timeout."""
    pass


def _timeout_handler(signum: int, frame: object) -> None:
    raise _LLMTimeoutError("LLM inference timed out")
