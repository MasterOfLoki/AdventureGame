"""Score tracking and rank system."""

from __future__ import annotations

from engine.models.enums import ObjectProperty
from engine.state.game_state import GameState
from engine.world.world import World


class ScoringSystem:
    """Tracks score for collecting treasures and placing them in trophy case."""

    def __init__(self, world: World):
        self.world = world

    def check_treasure_score(self, state: GameState) -> tuple[int, str | None]:
        """Check if any new treasures should award points.
        Returns (points_awarded, message)."""
        points = 0
        messages = []

        for obj in self.world.all_objects():
            if obj.score_value <= 0:
                continue

            score_flag = f"scored_{obj.id}"
            if score_flag in state.flags:
                continue

            # Award points for picking up treasure
            pickup_flag = f"picked_up_{obj.id}"
            if obj.id in state.inventory and pickup_flag not in state.flags:
                state.flags.add(pickup_flag)

            # Award points for placing in trophy case
            obj_state = state.object_states.get(obj.id)
            if obj_state and obj_state.parent_object == "trophy_case":
                if score_flag not in state.flags:
                    state.flags.add(score_flag)
                    points += obj.score_value
                    messages.append(f"[Your score just went up by {obj.score_value} points.]")

        if points > 0:
            state.score += points
            return points, "\n".join(messages)
        return 0, None

    def get_rank(self, state: GameState) -> str:
        """Get player's current rank based on score."""
        rank = "Beginner"
        for threshold, rank_name in sorted(self.world.config.ranks.items()):
            if state.score >= threshold:
                rank = rank_name
        return rank
