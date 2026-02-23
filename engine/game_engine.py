"""Main game engine orchestrator."""

from __future__ import annotations

from engine.actions.action_handler import ActionResult
from engine.actions.action_resolver import ActionResolver, ResolvedAction
from engine.actions.builtin_actions import _get_room_description, registry as builtin_registry
from engine.actions.effects import EffectApplier
from engine.actions.preconditions import PreconditionChecker
from engine.loader.game_loader import GameData, GameLoader
from engine.loader.validator import Validator
from engine.models.command import ParsedCommand
from engine.models.enums import ObjectProperty, TriggerType
from engine.parser.parser_interface import ParserContext, ParserInterface
from engine.state.game_state import GameState, NPCState, ObjectState
from engine.state.state_manager import StateManager
from engine.world.combat import CombatSystem
from engine.world.darkness import DarknessSystem
from engine.world.npc_controller import NPCController
from engine.world.scoring import ScoringSystem
from engine.world.world import World


class GameEngine:
    """Main game engine that orchestrates all systems."""

    def __init__(
        self,
        game_dir: str,
        parser: ParserInterface,
        save_dir: str = "saves",
        debug: bool = False,
    ):
        self.parser = parser
        self.debug = debug
        self.state_manager = StateManager(save_dir)

        # Load and validate game data
        loader = GameLoader(game_dir)
        self.game_data: GameData = loader.load()
        validator = Validator()
        errors = validator.validate(self.game_data)
        if errors:
            raise ValueError(
                f"Game data validation failed:\n"
                + "\n".join(f"  - {e.message}" for e in errors)
            )

        # Initialize systems
        self.world = World(self.game_data)
        self.resolver = ActionResolver(self.world)
        self.preconditions = PreconditionChecker()
        self.effects = EffectApplier()
        self.darkness = DarknessSystem()
        self.scoring = ScoringSystem(self.world)
        self.npc_controller = NPCController(self.world)
        self.combat = CombatSystem(self.world)
        self.action_registry = builtin_registry

        # Initialize state
        self.state = self._create_initial_state()

    def _create_initial_state(self) -> GameState:
        """Create the initial game state from game data."""
        state = GameState(current_room=self.world.config.starting_room)

        # Initialize object states
        for obj in self.world.all_objects():
            obj_state = ObjectState(
                location=obj.location,
                parent_object=obj.parent_object,
                properties=set(obj.properties),
            )
            state.object_states[obj.id] = obj_state

        # Initialize NPC states
        for npc in self.world.all_npcs():
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

    def start_game(self) -> str:
        """Start the game and return intro text + first room description."""
        parts = []
        if self.world.config.intro_text:
            parts.append(self.world.config.intro_text)

        room_desc = _get_room_description(
            self.state.current_room, self.state, self.world, force_long=True
        )
        parts.append(room_desc)
        self.state.visited_rooms.add(self.state.current_room)
        return "\n\n".join(parts)

    def process_input(self, input_text: str) -> str:
        """Process player input and return game output."""
        if not self.state.player_alive:
            return "You are dead. Type 'quit' to exit or 'restore' to load a save."

        # Build parser context
        context = self._build_parser_context()

        # Parse input
        command = self.parser.parse(input_text, context)
        if self.debug:
            print(f"[DEBUG] Parsed: {command.model_dump()}")

        # Handle meta-commands
        meta_result = self._handle_meta_command(command)
        if meta_result is not None:
            return meta_result

        # Resolve command to exact targets
        resolved = self.resolver.resolve(command, self.state)
        if isinstance(resolved, str):
            return resolved  # Error message

        if self.debug:
            print(
                f"[DEBUG] Resolved: verb={resolved.verb_id} "
                f"obj={resolved.direct_object_id} "
                f"indirect={resolved.indirect_object_id} "
                f"npc={resolved.npc_target_id}"
            )

        # Update command with resolved IDs for action handlers
        resolved_command = ParsedCommand(
            verb=resolved.verb_id,
            direct_object=resolved.direct_object_id or resolved.npc_target_id or command.direct_object,
            indirect_object=resolved.indirect_object_id or command.indirect_object,
            preposition=command.preposition,
            direction=command.direction,
            raw_input=command.raw_input,
        )

        # Check darkness before action (only allow certain verbs in dark)
        if self.darkness.is_dark(self.state, self.world):
            allowed_in_dark = {"look", "inventory", "turn_on", "quit", "save", "restore", "score", "wait"}
            if resolved.verb_id not in allowed_in_dark:
                # Going is allowed but risky
                if resolved.verb_id != "go":
                    return self.darkness.get_dark_description(self.state, self.world)

        # Run pre-action events
        event_messages = self._run_events(
            TriggerType.BEFORE_ACTION,
            verb_id=resolved.verb_id,
            direct_object_id=resolved.direct_object_id,
        )
        # Check if any event blocked the action
        for msg in event_messages:
            if msg == "__BLOCKED__":
                event_messages.remove("__BLOCKED__")
                return "\n".join(event_messages) if event_messages else ""

        # Execute action handler
        handler = self.action_registry.get_handler(resolved.verb_id)
        if not handler:
            return f"I don't know how to do that."

        result = handler(resolved_command, self.state, self.world)

        # Check for quit
        if result.message == "__QUIT__":
            return "__QUIT__"

        # Run post-action events
        post_messages = self._run_events(
            TriggerType.AFTER_ACTION,
            verb_id=resolved.verb_id,
            direct_object_id=resolved.direct_object_id,
        )

        # Increment turn counter
        self.state.turns += 1

        # Tick systems
        system_messages = self._tick_systems()

        # Check scoring
        _, score_msg = self.scoring.check_treasure_score(self.state)

        # Compile output
        all_messages = list(event_messages)
        if result.message:
            all_messages.append(result.full_message)
        all_messages.extend(post_messages)
        all_messages.extend(system_messages)
        if score_msg:
            all_messages.append(score_msg)

        return "\n".join(msg for msg in all_messages if msg)

    def _build_parser_context(self) -> ParserContext:
        """Build context for the parser with visible objects, exits, etc."""
        room = self.world.get_room(self.state.current_room)

        # Visible objects
        visible = []
        for obj_id in self.state.objects_in_room(self.state.current_room):
            obj = self.world.get_object(obj_id)
            if obj and not self.state.has_object_property(obj_id, ObjectProperty.HIDDEN):
                visible.append(obj.name)
                # Also include contents of open containers
                if self.state.has_object_property(obj_id, ObjectProperty.OPEN):
                    for child_id in self.state.objects_in_container(obj_id):
                        child = self.world.get_object(child_id)
                        if child:
                            visible.append(child.name)

        # Inventory names
        inv_names = []
        for obj_id in self.state.inventory:
            obj = self.world.get_object(obj_id)
            if obj:
                inv_names.append(obj.name)

        # Exits
        exits = []
        if room:
            for exit_ in room.exits:
                if not exit_.hidden:
                    exits.append(exit_.direction.value)

        # Valid verbs
        verb_names = []
        for verb in self.world.all_verbs():
            verb_names.extend(verb.names[:2])  # First 2 names for each verb

        # NPCs
        npc_names = []
        for npc_id in self.state.npc_in_room(self.state.current_room):
            npc = self.world.get_npc(npc_id)
            if npc:
                npc_names.append(npc.name)

        return ParserContext(
            visible_objects=visible,
            inventory=inv_names,
            exits=exits,
            valid_verbs=verb_names,
            npc_names=npc_names,
        )

    def _handle_meta_command(self, command: ParsedCommand) -> str | None:
        """Handle save/restore/quit commands. Returns message or None."""
        if command.verb == "save":
            slot = command.direct_object or "quicksave"
            self.state_manager.save(self.state, slot)
            return f"Game saved to slot '{slot}'."

        if command.verb == "restore":
            slot = command.direct_object or "quicksave"
            try:
                self.state = self.state_manager.load(slot)
                room_desc = _get_room_description(
                    self.state.current_room, self.state, self.world, force_long=True
                )
                return f"Game restored from slot '{slot}'.\n\n{room_desc}"
            except FileNotFoundError:
                return f"No save found in slot '{slot}'."

        return None

    def _run_events(self, trigger: TriggerType, **context) -> list[str]:
        """Run events matching the trigger and return messages."""
        messages = []
        events = self.world.get_events_for_trigger(trigger)

        for event in events:
            if event.once and event.id in self.state.fired_events:
                continue

            if self.preconditions.check_all(event.conditions, self.state, **context):
                effect_messages = self.effects.apply_all(event.effects, self.state)
                messages.extend(effect_messages)
                if event.once:
                    self.state.fired_events.add(event.id)

                if self.debug:
                    print(f"[DEBUG] Event fired: {event.id}")

        return messages

    def _tick_systems(self) -> list[str]:
        """Run per-turn system updates. Returns messages."""
        messages = []

        # Room entry events
        entry_messages = self._run_events(TriggerType.ENTER_ROOM)
        messages.extend(entry_messages)

        # Each-turn events
        turn_messages = self._run_events(TriggerType.EACH_TURN)
        messages.extend(turn_messages)

        # Light source fuel
        light_msg = self.darkness.tick_light_sources(self.state, self.world)
        if light_msg:
            messages.append(light_msg)

        # Darkness/grue check
        dark_msg = self.darkness.tick(self.state, self.world)
        if dark_msg:
            messages.append(dark_msg)

        # NPC behavior
        npc_messages = self.npc_controller.tick(self.state)
        messages.extend(npc_messages)

        # Combat from hostile NPCs
        for npc in self.world.all_npcs():
            npc_state = self.state.npc_states.get(npc.id)
            if (
                npc_state
                and npc_state.alive
                and npc_state.location == self.state.current_room
                and npc.attitude.value == "hostile"
            ):
                combat_msg = self.combat.npc_attack_player(npc.id, self.state)
                if combat_msg:
                    messages.append(combat_msg)

        return messages
