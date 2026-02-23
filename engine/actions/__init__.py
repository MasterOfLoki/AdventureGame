"""Action system for handling game verbs."""

from __future__ import annotations

from engine.actions.action_handler import ActionHandler, ActionResult
from engine.actions.action_registry import ActionRegistry
from engine.actions.action_resolver import ActionResolver, ResolvedAction
from engine.actions.preconditions import PreconditionChecker
from engine.actions.effects import EffectApplier
from engine.actions.builtin_actions import registry as builtin_registry

__all__ = [
    "ActionHandler",
    "ActionResult",
    "ActionRegistry",
    "ActionResolver",
    "ResolvedAction",
    "PreconditionChecker",
    "EffectApplier",
    "builtin_registry",
]
