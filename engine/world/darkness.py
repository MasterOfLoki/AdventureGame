"""Light and darkness mechanics including the grue."""

from __future__ import annotations

from engine.models.enums import ObjectProperty
from engine.state.game_state import GameState
from engine.world.world import World


class DarknessSystem:
    """Manages light/dark state and grue encounters."""

    def is_dark(self, state: GameState, world: World) -> bool:
        """Check if the current room is dark (no light source available)."""
        room = world.get_room(state.current_room)
        if not room or not room.is_dark:
            return False

        # Check if player has a lit light source
        for obj_id in state.inventory:
            if state.has_object_property(obj_id, ObjectProperty.LIT):
                return False

        # Check if room has a lit light source
        for obj_id in state.objects_in_room(state.current_room):
            if state.has_object_property(obj_id, ObjectProperty.LIT):
                return False

        return True

    def get_dark_description(self, state: GameState, world: World) -> str:
        room = world.get_room(state.current_room)
        if room:
            return room.dark_description
        return "It is pitch black. You are likely to be eaten by a grue."

    def tick(self, state: GameState, world: World) -> str | None:
        """Process darkness each turn. Returns message or None."""
        if not self.is_dark(state, world):
            state.dark_turns = 0
            return None

        state.dark_turns += 1
        if state.dark_turns == 1:
            return "It is pitch black. You are likely to be eaten by a grue."
        elif state.dark_turns >= 2:
            state.player_alive = False
            return (
                "Oh no! You have walked into the slavering fangs of a lurking grue!\n"
                "\n   **** You have died ****"
            )
        return None

    def tick_light_sources(self, state: GameState, world: World) -> str | None:
        """Decrement fuel on lit light sources. Returns warning message."""
        for obj_id in list(state.inventory) + state.objects_in_room(state.current_room):
            if not state.has_object_property(obj_id, ObjectProperty.LIT):
                continue
            obj = world.get_object(obj_id)
            if not obj or obj.light_fuel < 0:
                continue  # Infinite fuel

            # Track fuel in counters
            fuel_key = f"fuel_{obj_id}"
            fuel = state.counters.get(fuel_key, obj.light_fuel)
            fuel -= 1
            state.counters[fuel_key] = fuel

            if fuel <= 0:
                state.remove_object_property(obj_id, ObjectProperty.LIT)
                return f"The {obj.name} has run out of power."
            elif fuel <= 20:
                return f"The {obj.name} is getting dim."

        return None
