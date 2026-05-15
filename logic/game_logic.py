from __future__ import annotations

from typing import Any

from models.difference_region import DifferenceRegion


class GameLogic:
    """
    Encapsulates scoring, mistake tracking, click evaluation, and game state rules.
    """

    def __init__(self, max_mistakes: int = 3) -> None:
        self._max_mistakes = max_mistakes
        self._mistakes = 0
        self._game_over = False
        self._differences: list[DifferenceRegion] = []

    # -------------------------
    # Properties
    # -------------------------
    @property
    def max_mistakes(self) -> int:
        return self._max_mistakes

    @property
    def mistakes(self) -> int:
        return self._mistakes

    @property
    def game_over(self) -> bool:
        return self._game_over

    @property
    def differences(self) -> list[DifferenceRegion]:
        return self._differences

    # -------------------------
    # Setup / Reset
    # -------------------------
    def reset(self) -> None:
        self._mistakes = 0
        self._game_over = False
        self._differences = []

    def set_differences(self, differences: list[DifferenceRegion]) -> None:
        """
        Load new round differences and reset state.
        """
        self.reset()
        self._differences = differences

    # -------------------------
    # Game State Helpers
    # -------------------------
    def total_differences(self) -> int:
        return len(self._differences)

    def found_count(self) -> int:
        return sum(1 for r in self._differences if r.is_found)

    def remaining_count(self) -> int:
        return self.total_differences() - self.found_count()

    def can_continue(self) -> bool:
        return not self._game_over

    # -------------------------
    # Click Handling
    # -------------------------
    def process_click(self, x: int, y: int, tolerance: int = 12) -> dict[str, Any]:
        """
        Evaluate click position.

        Returns:
            {
                "status": "inactive" | "found" | "already_found" | "miss" | "win" | "lose",
                "region": DifferenceRegion (optional)
            }
        """

        if self._game_over or not self._differences:
            return {"status": "inactive"}

        # Check against all regions
        for region in self._differences:
            if region.contains_point(x, y, tolerance=tolerance):

                # Already found → no penalty
                if region.is_found:
                    return {"status": "already_found", "region": region}

                # Mark as found
                region.is_found = True

                # Check win condition
                if self.remaining_count() == 0:
                    self._game_over = True
                    return {"status": "win", "region": region}

                return {"status": "found", "region": region}

        # Miss case
        self._mistakes += 1

        if self._mistakes >= self._max_mistakes:
            self._game_over = True
            return {"status": "lose"}

        return {"status": "miss"}

    # -------------------------
    # Reveal Remaining
    # -------------------------
    def reveal_remaining(self) -> list[DifferenceRegion]:
        """
        Reveal all unfound differences and end game.
        """
        remaining = []

        for region in self._differences:
            if not region.is_found:
                region.is_found = True
                remaining.append(region)

        self._game_over = True
        return remaining