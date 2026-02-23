"""Apply event effects to game state."""

from __future__ import annotations

from engine.models.enums import EffectType, ObjectProperty
from engine.models.event import Effect
from engine.state.game_state import GameState


class EffectApplier:
    """Applies effects to mutate game state."""

    def apply(self, effect: Effect, state: GameState) -> str | None:
        """Apply an effect and return any message to display."""
        t = effect.type
        if t == EffectType.PRINT_MESSAGE:
            return str(effect.value)
        elif t == EffectType.MOVE_OBJECT:
            state.set_object_location(effect.target, str(effect.value))
            if str(effect.value) == "player":
                if effect.target not in state.inventory:
                    state.inventory.append(effect.target)
                state.set_object_location(effect.target, None)
            elif effect.target in state.inventory:
                state.inventory.remove(effect.target)
        elif t == EffectType.MOVE_PLAYER:
            state.current_room = effect.target
        elif t == EffectType.SET_FLAG:
            state.flags.add(effect.target)
        elif t == EffectType.CLEAR_FLAG:
            state.flags.discard(effect.target)
        elif t == EffectType.INCREMENT_COUNTER:
            current = state.counters.get(effect.target, 0)
            state.counters[effect.target] = current + int(effect.value or 1)
        elif t == EffectType.SET_COUNTER:
            state.counters[effect.target] = int(effect.value)
        elif t == EffectType.ADD_SCORE:
            state.score += int(effect.value)
        elif t == EffectType.SET_OBJECT_PROPERTY:
            prop = ObjectProperty(str(effect.value))
            state.add_object_property(effect.target, prop)
        elif t == EffectType.CLEAR_OBJECT_PROPERTY:
            prop = ObjectProperty(str(effect.value))
            state.remove_object_property(effect.target, prop)
        elif t == EffectType.KILL_PLAYER:
            state.player_alive = False
            return str(effect.value) if effect.value else "You have died."
        elif t == EffectType.DESTROY_OBJECT:
            state.set_object_location(effect.target, "destroyed")
            if effect.target in state.inventory:
                state.inventory.remove(effect.target)
        elif t == EffectType.REVEAL_OBJECT:
            state.remove_object_property(effect.target, ObjectProperty.HIDDEN)
        return None

    def apply_all(self, effects: list[Effect], state: GameState) -> list[str]:
        """Apply all effects and return messages."""
        messages = []
        for effect in effects:
            msg = self.apply(effect, state)
            if msg:
                messages.append(msg)
        return messages
