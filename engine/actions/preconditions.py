"""Evaluate event conditions against game state."""

from __future__ import annotations

from engine.models.enums import ConditionType, ObjectProperty
from engine.models.event import Condition
from engine.state.game_state import GameState


class PreconditionChecker:
    """Evaluates conditions against current game state."""

    def check(self, condition: Condition, state: GameState, **context) -> bool:
        t = condition.type
        if t == ConditionType.PLAYER_IN_ROOM:
            return state.current_room == condition.target
        elif t == ConditionType.PLAYER_HAS_ITEM:
            return state.player_has(condition.target)
        elif t == ConditionType.OBJECT_IN_ROOM:
            room = str(condition.value) if condition.value else state.current_room
            return condition.target in state.objects_in_room(room)
        elif t == ConditionType.OBJECT_HAS_PROPERTY:
            prop = ObjectProperty(str(condition.value))
            return state.has_object_property(condition.target, prop)
        elif t == ConditionType.FLAG_SET:
            return condition.target in state.flags
        elif t == ConditionType.FLAG_NOT_SET:
            return condition.target not in state.flags
        elif t == ConditionType.COUNTER_GTE:
            return state.counters.get(condition.target, 0) >= int(condition.value)
        elif t == ConditionType.COUNTER_LTE:
            return state.counters.get(condition.target, 0) <= int(condition.value)
        elif t == ConditionType.COUNTER_EQ:
            return state.counters.get(condition.target, 0) == int(condition.value)
        elif t == ConditionType.ACTION_IS:
            return context.get("verb_id") == condition.target
        elif t == ConditionType.ACTION_TARGET_IS:
            return context.get("direct_object_id") == condition.target
        return False

    def check_all(
        self, conditions: list[Condition], state: GameState, **context
    ) -> bool:
        return all(self.check(c, state, **context) for c in conditions)
