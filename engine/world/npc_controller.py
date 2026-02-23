"""NPC behavior controller - handles NPC actions each turn."""

from __future__ import annotations

import random

from engine.models.enums import ObjectProperty
from engine.state.game_state import GameState
from engine.world.world import World


class NPCController:
    """Controls NPC behavior during each game turn."""

    def __init__(self, world: World):
        self.world = world

    def tick(self, state: GameState) -> list[str]:
        """Process all NPC actions for a turn. Returns messages."""
        messages = []
        for npc in self.world.all_npcs():
            npc_state = state.npc_states.get(npc.id)
            if not npc_state or not npc_state.alive:
                continue

            # Wandering behavior
            if npc.behavior.wanders and npc.behavior.wander_rooms:
                msg = self._handle_wander(npc.id, state)
                if msg:
                    messages.append(msg)

            # Stealing behavior
            if npc.behavior.steals_items and npc_state.location == state.current_room:
                msg = self._handle_steal(npc.id, state)
                if msg:
                    messages.append(msg)

        return messages

    def _handle_wander(self, npc_id: str, state: GameState) -> str | None:
        """Move NPC to a random adjacent room from their wander list."""
        npc = self.world.get_npc(npc_id)
        npc_state = state.npc_states[npc_id]
        if not npc or not npc_state.location:
            return None

        # 30% chance to move each turn
        if random.random() > 0.3:
            return None

        possible = [r for r in npc.behavior.wander_rooms if r != npc_state.location]
        if not possible:
            return None

        old_room = npc_state.location
        new_room = random.choice(possible)
        npc_state.location = new_room

        # Message if player can see the movement
        if old_room == state.current_room:
            return f"The {npc.name} slips away."
        elif new_room == state.current_room:
            return f"A {npc.name} appears."

        return None

    def _handle_steal(self, npc_id: str, state: GameState) -> str | None:
        """NPC attempts to steal a valuable item from the player."""
        npc = self.world.get_npc(npc_id)
        npc_state = state.npc_states[npc_id]
        if not npc:
            return None

        # 25% chance to steal each turn
        if random.random() > 0.25:
            return None

        # Find valuable items in player inventory
        valuable = []
        for obj_id in state.inventory:
            obj = self.world.get_object(obj_id)
            if obj and obj.score_value > 0:
                valuable.append(obj_id)

        if not valuable:
            return None

        stolen_id = random.choice(valuable)
        stolen_obj = self.world.get_object(stolen_id)
        state.inventory.remove(stolen_id)
        npc_state.inventory.append(stolen_id)
        state.set_object_location(stolen_id, None)

        stolen_name = stolen_obj.name if stolen_obj else stolen_id
        return f"The {npc.name} snatches the {stolen_name} from you!"
