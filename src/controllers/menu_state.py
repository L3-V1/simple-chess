from __future__ import annotations

from dataclasses import dataclass

import chess

from src.core import EloRating


@dataclass
class MenuSelection:
    """Store the current menu selections for color and AI rating."""

    rating: EloRating
    color: chess.Color

    def select_color(self, color: chess.Color) -> bool:
        """Update the selected color and report whether it changed."""
        if color == self.color:
            return False
        self.color = color
        return True

    def select_rating(self, rating: EloRating) -> None:
        """Update the selected AI rating."""
        self.rating = rating
