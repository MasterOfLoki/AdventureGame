"""Mutable game state tracking player progress, object locations, etc."""

from __future__ import annotations

from pydantic import BaseModel, Field

from engine.models.enums import ObjectProperty


class NPCState(BaseModel):
    """Runtime state for an NPC."""
    location: str | None = None
    health: int = 10
    alive: bool = True
    inventory: list[str] = Field(default_factory=list)
    attitude: str = "neutral"


class ObjectState(BaseModel):
    """Runtime state for a game object."""
    location: str | None = None
    parent_object: str | None = None
    properties: set[ObjectProperty] = Field(default_factory=set)


class GameState(BaseModel):
    """All mutable runtime state for a game session."""
    current_room: str
    inventory: list[str] = Field(default_factory=list)
    score: int = 0
    turns: int = 0
    flags: set[str] = Field(default_factory=set)
    counters: dict[str, int] = Field(default_factory=dict)
    visited_rooms: set[str] = Field(default_factory=set)
    object_states: dict[str, ObjectState] = Field(default_factory=dict)
    npc_states: dict[str, NPCState] = Field(default_factory=dict)
    fired_events: set[str] = Field(default_factory=set)
    player_alive: bool = True
    player_health: int = 10
    dark_turns: int = 0

    def get_object_location(self, object_id: str) -> str | None:
        if object_id in self.object_states:
            return self.object_states[object_id].location
        return None

    def get_object_properties(self, object_id: str) -> set[ObjectProperty]:
        if object_id in self.object_states:
            return self.object_states[object_id].properties
        return set()

    def set_object_location(self, object_id: str, location: str | None):
        if object_id not in self.object_states:
            self.object_states[object_id] = ObjectState(location=location)
        else:
            self.object_states[object_id].location = location
        # Also clear parent_object when moving to a room/player
        if location and location != "destroyed":
            self.object_states[object_id].parent_object = None

    def set_object_parent(self, object_id: str, parent_id: str | None):
        if object_id not in self.object_states:
            self.object_states[object_id] = ObjectState()
        self.object_states[object_id].parent_object = parent_id
        if parent_id:
            self.object_states[object_id].location = None

    def add_object_property(self, object_id: str, prop: ObjectProperty):
        if object_id not in self.object_states:
            self.object_states[object_id] = ObjectState()
        self.object_states[object_id].properties.add(prop)

    def remove_object_property(self, object_id: str, prop: ObjectProperty):
        if object_id in self.object_states:
            self.object_states[object_id].properties.discard(prop)

    def has_object_property(self, object_id: str, prop: ObjectProperty) -> bool:
        if object_id in self.object_states:
            return prop in self.object_states[object_id].properties
        return False

    def objects_in_room(self, room_id: str) -> list[str]:
        return [
            oid for oid, state in self.object_states.items()
            if state.location == room_id
        ]

    def objects_in_container(self, container_id: str) -> list[str]:
        return [
            oid for oid, state in self.object_states.items()
            if state.parent_object == container_id
        ]

    def player_has(self, object_id: str) -> bool:
        return object_id in self.inventory

    def npc_in_room(self, room_id: str) -> list[str]:
        return [
            nid for nid, state in self.npc_states.items()
            if state.location == room_id and state.alive
        ]
