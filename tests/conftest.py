"""Shared test fixtures."""

from __future__ import annotations

import os
from pathlib import Path

import pytest

from engine.game_engine import GameEngine
from engine.loader import GameLoader
from engine.parser.fallback_parser import FallbackParser
from engine.state.game_state import GameState, ObjectState
from engine.world.world import World
from engine.models.enums import ObjectProperty

FIXTURES_DIR = Path(__file__).parent / "fixtures"
TINY_WORLD_DIR = FIXTURES_DIR / "tiny_world"


@pytest.fixture
def tiny_world_dir():
    return str(TINY_WORLD_DIR)


@pytest.fixture
def game_data():
    loader = GameLoader(TINY_WORLD_DIR)
    return loader.load()


@pytest.fixture
def world(game_data):
    return World(game_data)


@pytest.fixture
def state(game_data, world):
    """Create an initialized game state for the tiny world."""
    state = GameState(current_room=world.config.starting_room)
    for obj in world.all_objects():
        obj_state = ObjectState(
            location=obj.location,
            parent_object=obj.parent_object,
            properties=set(obj.properties),
        )
        state.object_states[obj.id] = obj_state
    from engine.state.game_state import NPCState
    for npc in world.all_npcs():
        npc_state = NPCState(
            location=npc.location,
            health=npc.health,
            alive=True,
            inventory=list(npc.inventory),
            attitude=npc.attitude.value,
        )
        state.npc_states[npc.id] = npc_state
    state.visited_rooms.add(state.current_room)
    return state


@pytest.fixture
def engine(tiny_world_dir):
    parser = FallbackParser()
    return GameEngine(
        game_dir=tiny_world_dir,
        parser=parser,
        save_dir=str(TINY_WORLD_DIR / ".test_saves"),
    )


@pytest.fixture(autouse=True)
def cleanup_saves():
    """Clean up test saves after each test."""
    yield
    save_dir = TINY_WORLD_DIR / ".test_saves"
    if save_dir.exists():
        for f in save_dir.glob("*.json"):
            f.unlink()
        save_dir.rmdir()
