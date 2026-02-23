"""Resolves parsed commands to exact object IDs."""

from __future__ import annotations

from engine.models.command import ParsedCommand
from engine.models.enums import ObjectProperty
from engine.state.game_state import GameState
from engine.world.world import World


class ResolvedAction:
    """A fully resolved action ready for execution."""

    def __init__(
        self,
        verb_id: str,
        command: ParsedCommand,
        direct_object_id: str | None = None,
        indirect_object_id: str | None = None,
        npc_target_id: str | None = None,
    ):
        self.verb_id = verb_id
        self.command = command
        self.direct_object_id = direct_object_id
        self.indirect_object_id = indirect_object_id
        self.npc_target_id = npc_target_id


class ActionResolver:
    """Resolves parsed commands into exact targets."""

    def __init__(self, world: World):
        self.world = world

    def resolve(
        self, command: ParsedCommand, state: GameState
    ) -> ResolvedAction | str:
        """Resolve a command. Returns ResolvedAction or error message string."""
        # Resolve verb
        verb_id = command.verb
        if not self.world.get_verb(verb_id):
            resolved = self.world.resolve_verb_name(verb_id)
            if resolved:
                verb_id = resolved
            else:
                return f"I don't know how to '{command.verb}'."

        direct_object_id = None
        indirect_object_id = None
        npc_target_id = None

        # Resolve direct object
        if command.direct_object:
            result = self._resolve_target(
                command.direct_object, state
            )
            if isinstance(result, str):
                return result
            obj_id, is_npc = result
            if is_npc:
                npc_target_id = obj_id
            else:
                direct_object_id = obj_id

        # Resolve indirect object
        if command.indirect_object:
            result = self._resolve_target(
                command.indirect_object, state
            )
            if isinstance(result, str):
                return result
            obj_id, is_npc = result
            if is_npc:
                npc_target_id = obj_id
            else:
                indirect_object_id = obj_id

        return ResolvedAction(
            verb_id=verb_id,
            command=command,
            direct_object_id=direct_object_id,
            indirect_object_id=indirect_object_id,
            npc_target_id=npc_target_id,
        )

    def _resolve_target(
        self, name: str, state: GameState
    ) -> tuple[str, bool] | str:
        """Resolve a name to (object_id, is_npc) or error string."""
        # Check NPCs first
        npc_ids = self.world.resolve_npc_name(name)
        for npc_id in npc_ids:
            npc_state = state.npc_states.get(npc_id)
            if npc_state and npc_state.location == state.current_room and npc_state.alive:
                return (npc_id, True)

        # Check objects
        object_ids = self.world.resolve_object_name(name)
        if not object_ids:
            # Try as object ID directly
            if self.world.get_object(name):
                object_ids = [name]
            else:
                return f"I don't see any '{name}' here."

        # Filter to accessible objects (in room, inventory, or inside open containers)
        accessible = []
        for oid in object_ids:
            if self._is_accessible(oid, state):
                accessible.append(oid)

        if not accessible:
            return f"I don't see any '{name}' here."
        if len(accessible) == 1:
            return (accessible[0], False)

        # Ambiguous - return first match (could improve disambiguation later)
        return (accessible[0], False)

    def _is_accessible(self, object_id: str, state: GameState) -> bool:
        """Check if an object is accessible to the player."""
        obj_state = state.object_states.get(object_id)
        if not obj_state:
            # Check initial location from world data
            obj = self.world.get_object(object_id)
            if not obj:
                return False
            return obj.location == state.current_room or object_id in state.inventory

        # In player inventory
        if object_id in state.inventory:
            return True

        # In current room
        if obj_state.location == state.current_room:
            # Check if hidden
            if state.has_object_property(object_id, ObjectProperty.HIDDEN):
                return False
            return True

        # Inside an open container in the room or inventory
        if obj_state.parent_object:
            parent_accessible = self._is_accessible(obj_state.parent_object, state)
            if not parent_accessible:
                return False
            parent_obj = self.world.get_object(obj_state.parent_object)
            if parent_obj and ObjectProperty.TRANSPARENT in (
                state.get_object_properties(obj_state.parent_object)
            ):
                return True
            return state.has_object_property(
                obj_state.parent_object, ObjectProperty.OPEN
            )

        return False
