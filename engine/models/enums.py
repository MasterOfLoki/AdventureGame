"""Enumerations used throughout the game engine."""

from __future__ import annotations

from enum import Enum


class Direction(str, Enum):
    NORTH = "north"
    SOUTH = "south"
    EAST = "east"
    WEST = "west"
    UP = "up"
    DOWN = "down"
    NORTHEAST = "northeast"
    NORTHWEST = "northwest"
    SOUTHEAST = "southeast"
    SOUTHWEST = "southwest"
    IN = "in"
    OUT = "out"


DIRECTION_ABBREVIATIONS: dict[str, Direction] = {
    "n": Direction.NORTH,
    "s": Direction.SOUTH,
    "e": Direction.EAST,
    "w": Direction.WEST,
    "u": Direction.UP,
    "d": Direction.DOWN,
    "ne": Direction.NORTHEAST,
    "nw": Direction.NORTHWEST,
    "se": Direction.SOUTHEAST,
    "sw": Direction.SOUTHWEST,
}


class ObjectProperty(str, Enum):
    """Properties that objects can have."""
    TAKEABLE = "takeable"
    OPENABLE = "openable"
    OPEN = "open"
    LOCKABLE = "lockable"
    LOCKED = "locked"
    CONTAINER = "container"
    SURFACE = "surface"
    LIGHT_SOURCE = "light_source"
    LIT = "lit"
    READABLE = "readable"
    EDIBLE = "edible"
    WEARABLE = "wearable"
    WORN = "worn"
    WEAPON = "weapon"
    SCENERY = "scenery"
    FIXED = "fixed"
    HIDDEN = "hidden"
    TRANSPARENT = "transparent"


class TriggerType(str, Enum):
    """When an event can fire."""
    BEFORE_ACTION = "before_action"
    AFTER_ACTION = "after_action"
    ENTER_ROOM = "enter_room"
    EACH_TURN = "each_turn"


class ConditionType(str, Enum):
    """Types of conditions for events."""
    PLAYER_IN_ROOM = "player_in_room"
    PLAYER_HAS_ITEM = "player_has_item"
    OBJECT_IN_ROOM = "object_in_room"
    OBJECT_HAS_PROPERTY = "object_has_property"
    FLAG_SET = "flag_set"
    FLAG_NOT_SET = "flag_not_set"
    COUNTER_GTE = "counter_gte"
    COUNTER_LTE = "counter_lte"
    COUNTER_EQ = "counter_eq"
    ACTION_IS = "action_is"
    ACTION_TARGET_IS = "action_target_is"


class EffectType(str, Enum):
    """Types of effects that events can apply."""
    PRINT_MESSAGE = "print_message"
    MOVE_OBJECT = "move_object"
    MOVE_PLAYER = "move_player"
    SET_FLAG = "set_flag"
    CLEAR_FLAG = "clear_flag"
    INCREMENT_COUNTER = "increment_counter"
    SET_COUNTER = "set_counter"
    ADD_SCORE = "add_score"
    SET_OBJECT_PROPERTY = "set_object_property"
    CLEAR_OBJECT_PROPERTY = "clear_object_property"
    KILL_PLAYER = "kill_player"
    BLOCK_ACTION = "block_action"
    REPLACE_ACTION_MESSAGE = "replace_action_message"
    ENABLE_EXIT = "enable_exit"
    DISABLE_EXIT = "disable_exit"
    DESTROY_OBJECT = "destroy_object"
    REVEAL_OBJECT = "reveal_object"


class NPCAttitude(str, Enum):
    FRIENDLY = "friendly"
    NEUTRAL = "neutral"
    HOSTILE = "hostile"
