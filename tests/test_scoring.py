"""Tests for scoring system."""

from __future__ import annotations

from engine.world.scoring import ScoringSystem


class TestScoring:
    def test_initial_rank(self, state, world):
        scoring = ScoringSystem(world)
        rank = scoring.get_rank(state)
        assert rank == "Beginner"

    def test_rank_progression(self, state, world):
        scoring = ScoringSystem(world)
        state.score = 5
        rank = scoring.get_rank(state)
        assert rank == "Adventurer"

    def test_trophy_case_score(self, state, world):
        scoring = ScoringSystem(world)
        # Put coin in trophy case
        state.object_states["trophy_case"].properties.add(
            __import__("engine.models.enums", fromlist=["ObjectProperty"]).ObjectProperty.OPEN
        )
        state.set_object_parent("coin", "trophy_case")
        points, msg = scoring.check_treasure_score(state)
        assert points == 5
        assert msg is not None
        assert state.score == 5

    def test_no_double_scoring(self, state, world):
        scoring = ScoringSystem(world)
        state.set_object_parent("coin", "trophy_case")
        scoring.check_treasure_score(state)
        # Score again — should get 0
        points, msg = scoring.check_treasure_score(state)
        assert points == 0
