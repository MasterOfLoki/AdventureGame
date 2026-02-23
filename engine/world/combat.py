"""Simple combat system for NPC encounters."""

from __future__ import annotations

import random

from engine.models.enums import ObjectProperty
from engine.state.game_state import GameState
from engine.world.world import World


class CombatSystem:
    """Handles combat between player and NPCs."""

    def __init__(self, world: World):
        self.world = world

    def get_player_weapon(self, state: GameState) -> tuple[str | None, int]:
        """Find the best weapon in player inventory. Returns (weapon_id, damage)."""
        best_id = None
        best_damage = 1  # Bare hands

        for obj_id in state.inventory:
            if state.has_object_property(obj_id, ObjectProperty.WEAPON):
                obj = self.world.get_object(obj_id)
                if obj and obj.damage > best_damage:
                    best_id = obj_id
                    best_damage = obj.damage

        return best_id, best_damage

    def npc_attack_player(self, npc_id: str, state: GameState) -> str | None:
        """NPC attacks the player. Returns message or None."""
        npc = self.world.get_npc(npc_id)
        npc_state = state.npc_states.get(npc_id)
        if not npc or not npc_state or not npc_state.alive:
            return None
        if npc_state.location != state.current_room:
            return None

        # 50% chance to attack each turn
        if random.random() > 0.5:
            miss_msg = npc.behavior.combat_messages.get(
                "miss", f"The {npc.name} swings and misses!"
            )
            return miss_msg

        damage = npc.damage
        state.player_health -= damage

        if state.player_health <= 0:
            state.player_alive = False
            return f"The {npc.name} strikes! You have died."

        hit_msg = npc.behavior.combat_messages.get(
            "hit", f"The {npc.name} hits you!"
        )
        return hit_msg
