"""Integration tests for the game engine."""

from __future__ import annotations


class TestEngineStartup:
    def test_start_game(self, engine):
        output = engine.start_game()
        assert "Start Room" in output

    def test_initial_state(self, engine):
        engine.start_game()
        assert engine.state.current_room == "start_room"
        assert engine.state.turns == 0


class TestEngineNavigation:
    def test_move_north(self, engine):
        engine.start_game()
        output = engine.process_input("north")
        assert engine.state.current_room == "north_room"

    def test_move_and_back(self, engine):
        engine.start_game()
        engine.process_input("north")
        engine.process_input("south")
        assert engine.state.current_room == "start_room"


class TestEngineObjectInteraction:
    def test_take_and_drop(self, engine):
        engine.start_game()
        output = engine.process_input("take key")
        assert "Taken" in output
        assert "key" in engine.state.inventory

        output = engine.process_input("drop key")
        assert "Dropped" in output
        assert "key" not in engine.state.inventory

    def test_open_container(self, engine):
        engine.start_game()
        output = engine.process_input("open box")
        assert "gold coin" in output.lower() or "Opening" in output

    def test_inventory(self, engine):
        engine.start_game()
        output = engine.process_input("take key")
        output = engine.process_input("i")
        assert "brass key" in output

    def test_look(self, engine):
        engine.start_game()
        output = engine.process_input("look")
        assert "Start Room" in output


class TestEngineMeta:
    def test_save_and_restore(self, engine):
        engine.start_game()
        engine.process_input("take key")
        engine.process_input("save")

        engine.process_input("drop key")
        assert "key" not in engine.state.inventory

        engine.process_input("restore")
        assert "key" in engine.state.inventory

    def test_turn_counter(self, engine):
        engine.start_game()
        engine.process_input("look")
        engine.process_input("look")
        assert engine.state.turns == 2

    def test_quit(self, engine):
        engine.start_game()
        output = engine.process_input("quit")
        assert output == "__QUIT__"


class TestEngineScoring:
    def test_score_command(self, engine):
        engine.start_game()
        output = engine.process_input("score")
        assert "0" in output
        assert "Beginner" in output
