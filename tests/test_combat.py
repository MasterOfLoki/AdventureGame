"""Tests for combat system."""

from __future__ import annotations

import random

from engine.models.enums import ObjectProperty
from engine.world.combat import CombatSystem


class TestCombat:
    def test_get_player_weapon_bare_hands(self, state, world):
        cs = CombatSystem(world)
        weapon_id, damage = cs.get_player_weapon(state)
        assert weapon_id is None
        assert damage == 1

    def test_get_player_weapon_with_sword(self, state, world):
        cs = CombatSystem(world)
        state.inventory.append("sword")
        weapon_id, damage = cs.get_player_weapon(state)
        assert weapon_id == "sword"
        assert damage == 5

    def test_npc_attack_returns_message(self, state, world):
        cs = CombatSystem(world)
        state.current_room = "east_room"
        # Run several times — should always return a message (hit or miss)
        random.seed(42)
        msg = cs.npc_attack_player("guard", state)
        assert msg is not None
        # Either took damage or got a miss message
        assert state.player_health < 10 or "stumbles" in msg.lower() or "misses" in msg.lower()

    def test_npc_not_in_room(self, state, world):
        cs = CombatSystem(world)
        state.current_room = "start_room"  # guard is in east_room
        msg = cs.npc_attack_player("guard", state)
        assert msg is None
