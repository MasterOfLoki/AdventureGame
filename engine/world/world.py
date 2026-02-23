"""Immutable world data with indexed lookups."""

from __future__ import annotations

from engine.loader.game_loader import GameData
from engine.models import (
    Event,
    GameConfig,
    GameObject,
    NPC,
    Room,
    TriggerType,
    VerbDefinition,
)


class World:
    """Provides indexed access to immutable game data."""

    def __init__(self, data: GameData):
        self.config: GameConfig = data.config

        # Index rooms by ID
        self._rooms: dict[str, Room] = {r.id: r for r in data.rooms}

        # Index objects by ID
        self._objects: dict[str, GameObject] = {o.id: o for o in data.objects}

        # Build object name/alias lookup: name -> list of object IDs
        self._object_names: dict[str, list[str]] = {}
        for obj in data.objects:
            for name in [obj.name.lower()] + [a.lower() for a in obj.aliases]:
                self._object_names.setdefault(name, []).append(obj.id)

        # Index NPCs by ID
        self._npcs: dict[str, NPC] = {n.id: n for n in data.npcs}

        # Build NPC name/alias lookup
        self._npc_names: dict[str, list[str]] = {}
        for npc in data.npcs:
            for name in [npc.name.lower()] + [a.lower() for a in npc.aliases]:
                self._npc_names.setdefault(name, []).append(npc.id)

        # Index verbs by ID and names
        self._verbs: dict[str, VerbDefinition] = {v.id: v for v in data.verbs}
        self._verb_names: dict[str, str] = {}
        for verb in data.verbs:
            for name in verb.names:
                self._verb_names[name.lower()] = verb.id

        # Index events by trigger type
        self._events: dict[str, Event] = {e.id: e for e in data.events}
        self._events_by_trigger: dict[TriggerType, list[Event]] = {}
        for event in data.events:
            self._events_by_trigger.setdefault(event.trigger, []).append(event)
        # Sort by priority (higher first)
        for trigger in self._events_by_trigger:
            self._events_by_trigger[trigger].sort(
                key=lambda e: e.priority, reverse=True
            )

    def get_room(self, room_id: str) -> Room | None:
        return self._rooms.get(room_id)

    def get_object(self, object_id: str) -> GameObject | None:
        return self._objects.get(object_id)

    def get_npc(self, npc_id: str) -> NPC | None:
        return self._npcs.get(npc_id)

    def get_verb(self, verb_id: str) -> VerbDefinition | None:
        return self._verbs.get(verb_id)

    def resolve_verb_name(self, name: str) -> str | None:
        return self._verb_names.get(name.lower())

    def resolve_object_name(self, name: str) -> list[str]:
        return self._object_names.get(name.lower(), [])

    def resolve_npc_name(self, name: str) -> list[str]:
        return self._npc_names.get(name.lower(), [])

    def get_events_for_trigger(self, trigger: TriggerType) -> list[Event]:
        return self._events_by_trigger.get(trigger, [])

    def all_rooms(self) -> list[Room]:
        return list(self._rooms.values())

    def all_objects(self) -> list[GameObject]:
        return list(self._objects.values())

    def all_npcs(self) -> list[NPC]:
        return list(self._npcs.values())

    def all_verbs(self) -> list[VerbDefinition]:
        return list(self._verbs.values())
