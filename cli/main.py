"""CLI entry point for the adventure game."""

from __future__ import annotations

import argparse
import sys

from cli.text_interface import TextInterface
from engine.game_engine import GameEngine
from engine.parser.fallback_parser import FallbackParser


def create_parser_from_args(args) -> "ParserInterface":
    """Create the appropriate parser based on CLI arguments."""
    if args.parser == "llm":
        if not args.model:
            print("Error: --model is required when using --parser llm")
            sys.exit(1)
        from engine.parser.llm_parser import LLMParser
        return LLMParser(model_path=args.model)
    return FallbackParser()


def main():
    arg_parser = argparse.ArgumentParser(
        description="Adventure Game Engine",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    arg_parser.add_argument(
        "game_dir",
        help="Path to game data directory",
    )
    arg_parser.add_argument(
        "--parser",
        choices=["fallback", "llm"],
        default="fallback",
        help="Parser to use (default: fallback)",
    )
    arg_parser.add_argument(
        "--model",
        help="Path to LLM model file (required for --parser llm)",
    )
    arg_parser.add_argument(
        "--debug",
        action="store_true",
        help="Show debug output (parsed commands, state changes)",
    )
    arg_parser.add_argument(
        "--save-dir",
        default="saves",
        help="Directory for save files (default: saves)",
    )

    args = arg_parser.parse_args()

    # Create interface
    interface = TextInterface(debug=args.debug)

    # Create parser
    parser = create_parser_from_args(args)

    # Create engine
    try:
        engine = GameEngine(
            game_dir=args.game_dir,
            parser=parser,
            save_dir=args.save_dir,
            debug=args.debug,
        )
    except (FileNotFoundError, ValueError) as e:
        interface.show_error(f"Failed to load game: {e}")
        sys.exit(1)

    # Start game
    intro = engine.start_game()
    interface.show_title(engine.world.config.title)
    interface.show_room(intro)

    # Main game loop
    while True:
        input_text = interface.get_input()
        if not input_text:
            continue

        output = engine.process_input(input_text)

        if output == "__QUIT__":
            # Show final score
            rank = engine.scoring.get_rank(engine.state)
            interface.show_score(
                engine.state.score,
                engine.world.config.max_score,
                engine.state.turns,
                rank,
            )
            interface.show_text("Thank you for playing!")
            break

        if not engine.state.player_alive:
            interface.show_text(output)
            interface.show_death()
            rank = engine.scoring.get_rank(engine.state)
            interface.show_score(
                engine.state.score,
                engine.world.config.max_score,
                engine.state.turns,
                rank,
            )
            # Allow restore
            while True:
                interface.show_text("Would you like to restore a saved game? (yes/no)")
                answer = interface.get_input().lower()
                if answer in ("yes", "y"):
                    output = engine.process_input("restore")
                    interface.show_room(output)
                    break
                elif answer in ("no", "n", "quit", "q"):
                    interface.show_text("Thank you for playing!")
                    return
            continue

        # Check if the output looks like a room description (starts with room name)
        room = engine.world.get_room(engine.state.current_room)
        if room and output.startswith(room.name):
            interface.show_room(output)
        else:
            interface.show_text(output)


if __name__ == "__main__":
    main()
