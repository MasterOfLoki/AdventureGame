"""Natural language parsers."""

from __future__ import annotations

from engine.parser.parser_interface import ParserContext, ParserInterface
from engine.parser.fallback_parser import FallbackParser

__all__ = ["ParserContext", "ParserInterface", "FallbackParser"]
