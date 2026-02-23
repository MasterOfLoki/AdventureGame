"""Cross-reference validation for loaded game data."""

from __future__ import annotations

from engine.loader.game_loader import GameData


class ValidationError:
    def __init__(self, message: str):
        self.message = message

    def __repr__(self):
        return f"ValidationError({self.message!r})"


class Validator:
    """Validates cross-references in game data."""

    def validate(self, data: GameData) -> list[ValidationError]:
        errors: list[ValidationError] = []
        room_ids = {r.id for r in data.rooms}
        object_ids = {o.id for o in data.objects}
        npc_ids = {n.id for n in data.npcs}

        # Check starting room exists
        if data.config.starting_room not in room_ids:
            errors.append(ValidationError(
                f"Starting room '{data.config.starting_room}' not found"
            ))

        # Check exit targets exist
        for room in data.rooms:
            for exit_ in room.exits:
                if exit_.target_room not in room_ids:
                    errors.append(ValidationError(
                        f"Room '{room.id}' exit to unknown room '{exit_.target_room}'"
                    ))

        # Check object locations
        all_locations = room_ids | object_ids | {"player"}
        for obj in data.objects:
            if obj.location and obj.location not in all_locations:
                errors.append(ValidationError(
                    f"Object '{obj.id}' in unknown location '{obj.location}'"
                ))
            if obj.parent_object and obj.parent_object not in object_ids:
                errors.append(ValidationError(
                    f"Object '{obj.id}' has unknown parent '{obj.parent_object}'"
                ))
            if obj.key_id and obj.key_id not in object_ids:
                errors.append(ValidationError(
                    f"Object '{obj.id}' has unknown key '{obj.key_id}'"
                ))

        # Check NPC locations
        for npc in data.npcs:
            if npc.location and npc.location not in room_ids:
                errors.append(ValidationError(
                    f"NPC '{npc.id}' in unknown room '{npc.location}'"
                ))
            for room_id in npc.behavior.wander_rooms:
                if room_id not in room_ids:
                    errors.append(ValidationError(
                        f"NPC '{npc.id}' wander room '{room_id}' not found"
                    ))

        return errors
