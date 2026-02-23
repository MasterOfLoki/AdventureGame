"""Registry mapping verb IDs to handler functions."""

from __future__ import annotations

from typing import Callable

from engine.actions.action_handler import ActionHandler


class ActionRegistry:
    """Maps verb IDs to their handler functions."""

    def __init__(self):
        self._handlers: dict[str, ActionHandler] = {}

    def register(self, verb_id: str, handler: ActionHandler):
        self._handlers[verb_id] = handler

    def get_handler(self, verb_id: str) -> ActionHandler | None:
        return self._handlers.get(verb_id)

    def register_decorator(self, verb_id: str) -> Callable:
        def decorator(fn: ActionHandler) -> ActionHandler:
            self._handlers[verb_id] = fn
            return fn
        return decorator

    @property
    def registered_verbs(self) -> list[str]:
        return list(self._handlers.keys())
