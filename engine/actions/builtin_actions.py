"""Built-in action handlers for standard verbs."""

from __future__ import annotations

from engine.actions.action_handler import ActionResult
from engine.actions.action_registry import ActionRegistry
from engine.models.command import ParsedCommand
from engine.models.enums import Direction, ObjectProperty
from engine.state.game_state import GameState
from engine.world.world import World

registry = ActionRegistry()


def _get_room_description(
    room_id: str, state: GameState, world: World, force_long: bool = False
) -> str:
    """Build a full room description including objects and NPCs."""
    room = world.get_room(room_id)
    if not room:
        return "You are nowhere."

    parts = [room.name]

    # Use long description on first visit or if forced
    if force_long or room_id not in state.visited_rooms:
        desc = room.first_visit_description or room.description
    else:
        desc = room.short_description or room.description
    parts.append(desc)

    # List objects in room
    room_objects = state.objects_in_room(room_id)
    for obj_id in room_objects:
        obj = world.get_object(obj_id)
        if obj and ObjectProperty.SCENERY not in state.get_object_properties(obj_id):
            if obj.description.room:
                parts.append(obj.description.room)
            else:
                parts.append(f"There is a {obj.name} here.")

    # List NPCs in room
    for npc_id in state.npc_in_room(room_id):
        npc = world.get_npc(npc_id)
        if npc:
            if npc.description:
                parts.append(npc.description)
            else:
                parts.append(f"A {npc.name} is here.")

    return "\n".join(parts)


@registry.register_decorator("look")
def handle_look(
    command: ParsedCommand, state: GameState, world: World
) -> ActionResult:
    desc = _get_room_description(state.current_room, state, world, force_long=True)
    return ActionResult(message=desc)


@registry.register_decorator("go")
def handle_go(
    command: ParsedCommand, state: GameState, world: World
) -> ActionResult:
    direction_str = command.direction or command.direct_object
    if not direction_str:
        return ActionResult(message="Which direction?", success=False)

    # Parse direction
    try:
        direction = Direction(direction_str.lower())
    except ValueError:
        return ActionResult(
            message=f"'{direction_str}' is not a valid direction.", success=False
        )

    room = world.get_room(state.current_room)
    if not room:
        return ActionResult(message="You are nowhere.", success=False)

    # Find matching exit
    for exit_ in room.exits:
        if exit_.direction == direction:
            if exit_.hidden and f"exit_revealed_{room.id}_{direction.value}" not in state.flags:
                break  # Treat hidden exit as not found

            # Check exit conditions
            if exit_.condition:
                blocked = False
                if exit_.condition.flag and exit_.condition.flag not in state.flags:
                    blocked = True
                if exit_.condition.object_property and exit_.condition.object_id:
                    prop = ObjectProperty(exit_.condition.object_property)
                    if not state.has_object_property(exit_.condition.object_id, prop):
                        blocked = True
                if blocked:
                    return ActionResult(
                        message=exit_.condition.message_if_blocked, success=False
                    )

            # Move player
            state.current_room = exit_.target_room
            desc = _get_room_description(exit_.target_room, state, world)
            state.visited_rooms.add(exit_.target_room)
            return ActionResult(message=desc)

    return ActionResult(message="You can't go that way.", success=False)


@registry.register_decorator("take")
def handle_take(
    command: ParsedCommand, state: GameState, world: World
) -> ActionResult:
    obj_id = command.direct_object
    if not obj_id:
        return ActionResult(message="Take what?", success=False)

    # Resolve from world if needed
    obj = world.get_object(obj_id)
    if not obj:
        candidates = world.resolve_object_name(obj_id)
        if candidates:
            obj_id = candidates[0]
            obj = world.get_object(obj_id)
    if not obj:
        return ActionResult(message=f"I don't see any '{command.direct_object}' here.", success=False)

    if obj_id in state.inventory:
        return ActionResult(message="You already have that.", success=False)

    props = state.get_object_properties(obj_id)
    if ObjectProperty.FIXED in props or ObjectProperty.SCENERY in props:
        return ActionResult(message="You can't take that.", success=False)
    if ObjectProperty.TAKEABLE not in props:
        return ActionResult(message="You can't take that.", success=False)

    # Check inventory capacity
    if len(state.inventory) >= world.config.max_inventory_size:
        return ActionResult(message="You're carrying too many things.", success=False)

    state.inventory.append(obj_id)
    state.set_object_location(obj_id, None)
    state.set_object_parent(obj_id, None)
    return ActionResult(message="Taken.")


@registry.register_decorator("drop")
def handle_drop(
    command: ParsedCommand, state: GameState, world: World
) -> ActionResult:
    obj_id = command.direct_object
    if not obj_id:
        return ActionResult(message="Drop what?", success=False)

    if obj_id not in state.inventory:
        return ActionResult(message="You're not carrying that.", success=False)

    state.inventory.remove(obj_id)
    state.set_object_location(obj_id, state.current_room)
    return ActionResult(message="Dropped.")


@registry.register_decorator("inventory")
def handle_inventory(
    command: ParsedCommand, state: GameState, world: World
) -> ActionResult:
    if not state.inventory:
        return ActionResult(message="You are empty-handed.")

    lines = ["You are carrying:"]
    for obj_id in state.inventory:
        obj = world.get_object(obj_id)
        name = obj.name if obj else obj_id
        lines.append(f"  A {name}")
    return ActionResult(message="\n".join(lines))


@registry.register_decorator("examine")
def handle_examine(
    command: ParsedCommand, state: GameState, world: World
) -> ActionResult:
    obj_id = command.direct_object
    if not obj_id:
        return ActionResult(message="Examine what?", success=False)

    obj = world.get_object(obj_id)
    if not obj:
        # Try NPC
        npc = world.get_npc(obj_id)
        if npc:
            return ActionResult(message=npc.description or f"You see nothing special about the {npc.name}.")
        return ActionResult(message=f"I don't see any '{command.direct_object}' here.", success=False)

    parts = []
    if obj.description.examine:
        parts.append(obj.description.examine)
    else:
        parts.append(f"You see nothing special about the {obj.name}.")

    # If container and open, list contents
    if ObjectProperty.CONTAINER in state.get_object_properties(obj_id):
        if state.has_object_property(obj_id, ObjectProperty.OPEN):
            contents = state.objects_in_container(obj_id)
            if contents:
                parts.append(f"The {obj.name} contains:")
                for cid in contents:
                    cobj = world.get_object(cid)
                    cname = cobj.name if cobj else cid
                    parts.append(f"  A {cname}")
            else:
                parts.append(f"The {obj.name} is empty.")

    return ActionResult(message="\n".join(parts))


@registry.register_decorator("open")
def handle_open(
    command: ParsedCommand, state: GameState, world: World
) -> ActionResult:
    obj_id = command.direct_object
    if not obj_id:
        return ActionResult(message="Open what?", success=False)

    obj = world.get_object(obj_id)
    if not obj:
        return ActionResult(message=f"I don't see any '{command.direct_object}' here.", success=False)

    props = state.get_object_properties(obj_id)
    if ObjectProperty.OPENABLE not in props:
        return ActionResult(message="You can't open that.", success=False)
    if ObjectProperty.OPEN in props:
        return ActionResult(message="It's already open.", success=False)
    if ObjectProperty.LOCKED in props:
        return ActionResult(message="It's locked.", success=False)

    state.add_object_property(obj_id, ObjectProperty.OPEN)

    parts = ["Opened."]
    if obj.description.on_open:
        parts = [obj.description.on_open]

    # Show contents of containers
    if ObjectProperty.CONTAINER in props:
        contents = state.objects_in_container(obj_id)
        if contents:
            for cid in contents:
                cobj = world.get_object(cid)
                cname = cobj.name if cobj else cid
                parts.append(f"The {obj.name} contains a {cname}.")

    return ActionResult(message="\n".join(parts))


@registry.register_decorator("close")
def handle_close(
    command: ParsedCommand, state: GameState, world: World
) -> ActionResult:
    obj_id = command.direct_object
    if not obj_id:
        return ActionResult(message="Close what?", success=False)

    obj = world.get_object(obj_id)
    if not obj:
        return ActionResult(message=f"I don't see any '{command.direct_object}' here.", success=False)

    props = state.get_object_properties(obj_id)
    if ObjectProperty.OPENABLE not in props:
        return ActionResult(message="You can't close that.", success=False)
    if ObjectProperty.OPEN not in props:
        return ActionResult(message="It's already closed.", success=False)

    state.remove_object_property(obj_id, ObjectProperty.OPEN)
    return ActionResult(message="Closed.")


@registry.register_decorator("turn_on")
def handle_turn_on(
    command: ParsedCommand, state: GameState, world: World
) -> ActionResult:
    obj_id = command.direct_object
    if not obj_id:
        return ActionResult(message="Turn on what?", success=False)

    obj = world.get_object(obj_id)
    if not obj:
        return ActionResult(message=f"I don't see any '{command.direct_object}' here.", success=False)

    props = state.get_object_properties(obj_id)
    if ObjectProperty.LIGHT_SOURCE not in props:
        return ActionResult(message="You can't turn that on.", success=False)
    if ObjectProperty.LIT in props:
        return ActionResult(message="It's already on.", success=False)

    state.add_object_property(obj_id, ObjectProperty.LIT)
    return ActionResult(message=f"The {obj.name} is now on.")


@registry.register_decorator("turn_off")
def handle_turn_off(
    command: ParsedCommand, state: GameState, world: World
) -> ActionResult:
    obj_id = command.direct_object
    if not obj_id:
        return ActionResult(message="Turn off what?", success=False)

    obj = world.get_object(obj_id)
    if not obj:
        return ActionResult(message=f"I don't see any '{command.direct_object}' here.", success=False)

    props = state.get_object_properties(obj_id)
    if ObjectProperty.LIGHT_SOURCE not in props:
        return ActionResult(message="You can't turn that off.", success=False)
    if ObjectProperty.LIT not in props:
        return ActionResult(message="It's already off.", success=False)

    state.remove_object_property(obj_id, ObjectProperty.LIT)
    return ActionResult(message=f"The {obj.name} is now off.")


@registry.register_decorator("put")
def handle_put(
    command: ParsedCommand, state: GameState, world: World
) -> ActionResult:
    obj_id = command.direct_object
    container_id = command.indirect_object
    if not obj_id:
        return ActionResult(message="Put what?", success=False)
    if not container_id:
        return ActionResult(message="Where do you want to put it?", success=False)

    if obj_id not in state.inventory:
        return ActionResult(message="You're not carrying that.", success=False)

    container = world.get_object(container_id)
    if not container:
        return ActionResult(message=f"I don't see any '{command.indirect_object}' here.", success=False)

    container_props = state.get_object_properties(container_id)
    is_container = ObjectProperty.CONTAINER in container_props
    is_surface = ObjectProperty.SURFACE in container_props
    if not is_container and not is_surface:
        return ActionResult(message="You can't put things there.", success=False)

    if is_container and ObjectProperty.OPEN not in container_props:
        return ActionResult(message=f"The {container.name} is closed.", success=False)

    state.inventory.remove(obj_id)
    state.set_object_parent(obj_id, container_id)
    obj = world.get_object(obj_id)
    obj_name = obj.name if obj else obj_id
    if is_surface:
        return ActionResult(message=f"You put the {obj_name} on the {container.name}.")
    return ActionResult(message=f"You put the {obj_name} in the {container.name}.")


@registry.register_decorator("unlock")
def handle_unlock(
    command: ParsedCommand, state: GameState, world: World
) -> ActionResult:
    obj_id = command.direct_object
    key_id = command.indirect_object
    if not obj_id:
        return ActionResult(message="Unlock what?", success=False)

    obj = world.get_object(obj_id)
    if not obj:
        return ActionResult(message=f"I don't see any '{command.direct_object}' here.", success=False)

    props = state.get_object_properties(obj_id)
    if ObjectProperty.LOCKABLE not in props:
        return ActionResult(message="You can't unlock that.", success=False)
    if ObjectProperty.LOCKED not in props:
        return ActionResult(message="It's not locked.", success=False)

    # Check key
    if obj.key_id:
        if not key_id:
            return ActionResult(message="What do you want to unlock it with?", success=False)
        if key_id != obj.key_id:
            return ActionResult(message="That doesn't work.", success=False)
        if key_id not in state.inventory:
            return ActionResult(message="You don't have that.", success=False)

    state.remove_object_property(obj_id, ObjectProperty.LOCKED)
    return ActionResult(message="Unlocked.")


@registry.register_decorator("read")
def handle_read(
    command: ParsedCommand, state: GameState, world: World
) -> ActionResult:
    obj_id = command.direct_object
    if not obj_id:
        return ActionResult(message="Read what?", success=False)

    obj = world.get_object(obj_id)
    if not obj:
        return ActionResult(message=f"I don't see any '{command.direct_object}' here.", success=False)

    if ObjectProperty.READABLE not in state.get_object_properties(obj_id):
        return ActionResult(message="There's nothing to read on that.", success=False)

    if obj.description.on_read:
        return ActionResult(message=obj.description.on_read)
    return ActionResult(message="There's nothing written on it.")


@registry.register_decorator("eat")
def handle_eat(
    command: ParsedCommand, state: GameState, world: World
) -> ActionResult:
    obj_id = command.direct_object
    if not obj_id:
        return ActionResult(message="Eat what?", success=False)

    obj = world.get_object(obj_id)
    if not obj:
        return ActionResult(message=f"I don't see any '{command.direct_object}' here.", success=False)

    if ObjectProperty.EDIBLE not in state.get_object_properties(obj_id):
        return ActionResult(message="That's not something you can eat.", success=False)

    # Remove from inventory/world
    if obj_id in state.inventory:
        state.inventory.remove(obj_id)
    state.set_object_location(obj_id, "destroyed")
    return ActionResult(message=f"You eat the {obj.name}. Not bad.")


@registry.register_decorator("attack")
def handle_attack(
    command: ParsedCommand, state: GameState, world: World
) -> ActionResult:
    target = command.direct_object
    if not target:
        return ActionResult(message="Attack what?", success=False)

    # Check if target is NPC
    npc = world.get_npc(target)
    if not npc:
        npc_ids = world.resolve_npc_name(target)
        if npc_ids:
            npc = world.get_npc(npc_ids[0])
            target = npc_ids[0]
    if not npc:
        return ActionResult(message="Violence isn't the answer here.", success=False)

    npc_state = state.npc_states.get(target)
    if not npc_state or not npc_state.alive:
        return ActionResult(message="It's already dead.", success=False)
    if npc_state.location != state.current_room:
        return ActionResult(message="I don't see that here.", success=False)

    # Check weapon
    weapon_id = command.indirect_object
    weapon_damage = 1
    if weapon_id:
        weapon = world.get_object(weapon_id)
        if weapon and weapon.damage > 0:
            weapon_damage = weapon.damage
    else:
        # Check inventory for weapons
        for inv_id in state.inventory:
            inv_obj = world.get_object(inv_id)
            if inv_obj and ObjectProperty.WEAPON in state.get_object_properties(inv_id):
                weapon_damage = max(weapon_damage, inv_obj.damage)

    # Deal damage
    npc_state.health -= weapon_damage
    if npc_state.health <= 0:
        npc_state.alive = False
        if npc.death_flag:
            state.flags.add(npc.death_flag)
        msg = npc.death_message or f"The {npc.name} is dead!"
        # Drop NPC inventory
        for item_id in npc_state.inventory:
            state.set_object_location(item_id, state.current_room)
        npc_state.inventory.clear()
        return ActionResult(message=msg)

    # NPC fights back
    msgs = [f"You strike the {npc.name}!"]
    counter_msg = npc.behavior.combat_messages.get("counter", f"The {npc.name} strikes back!")
    msgs.append(counter_msg)
    state.player_health -= npc.damage
    if state.player_health <= 0:
        state.player_alive = False
        msgs.append("You have died.")
    return ActionResult(message="\n".join(msgs))


@registry.register_decorator("wait")
def handle_wait(
    command: ParsedCommand, state: GameState, world: World
) -> ActionResult:
    return ActionResult(message="Time passes.")


@registry.register_decorator("score")
def handle_score(
    command: ParsedCommand, state: GameState, world: World
) -> ActionResult:
    rank = "Beginner"
    for threshold, rank_name in sorted(world.config.ranks.items()):
        if state.score >= threshold:
            rank = rank_name
    return ActionResult(
        message=f"Your score is {state.score} (out of {world.config.max_score}). "
        f"This gives you the rank of {rank}."
    )


@registry.register_decorator("quit")
def handle_quit(
    command: ParsedCommand, state: GameState, world: World
) -> ActionResult:
    return ActionResult(message="__QUIT__")


@registry.register_decorator("move")
def handle_move(
    command: ParsedCommand, state: GameState, world: World
) -> ActionResult:
    """Move an object (like a rug) — distinct from 'go'."""
    obj_id = command.direct_object
    if not obj_id:
        return ActionResult(message="Move what?", success=False)

    obj = world.get_object(obj_id)
    if not obj:
        return ActionResult(message=f"I don't see any '{command.direct_object}' here.", success=False)

    # Moving is handled by events — if no event catches it, give generic response
    return ActionResult(message=f"Moving the {obj.name} reveals nothing special.")


@registry.register_decorator("take_from")
def handle_take_from(
    command: ParsedCommand, state: GameState, world: World
) -> ActionResult:
    """Take object from container."""
    obj_id = command.direct_object
    container_id = command.indirect_object
    if not obj_id:
        return ActionResult(message="Take what?", success=False)

    obj = world.get_object(obj_id)
    if not obj:
        return ActionResult(message=f"I don't see any '{command.direct_object}' here.", success=False)

    if obj_id in state.inventory:
        return ActionResult(message="You already have that.", success=False)

    props = state.get_object_properties(obj_id)
    if ObjectProperty.TAKEABLE not in props:
        return ActionResult(message="You can't take that.", success=False)

    state.inventory.append(obj_id)
    state.set_object_location(obj_id, None)
    state.set_object_parent(obj_id, None)
    return ActionResult(message="Taken.")
