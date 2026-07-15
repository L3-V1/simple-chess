from __future__ import annotations

from dataclasses import dataclass, field

import chess

from src.core import EloRating
from src.services import ComputerPlayer

from .game_session import GameSession


@dataclass
class GameRuntime:
    """Aggregate mutable match state used by the active game screen."""

    session: GameSession = field(default_factory=GameSession)
    selected_rating: EloRating = EloRating.ELO_1500
    human_color: chess.Color = chess.WHITE
    ai_is_thinking: bool = False
    computer_player: ComputerPlayer = field(init=False)

    def __post_init__(self) -> None:
        self.computer_player = ComputerPlayer(self.selected_rating)

    def apply_menu_selection(
        self,
        rating: EloRating,
        human_color: chess.Color,
    ) -> None:
        """Update match preferences selected in the menu."""
        self.selected_rating = rating
        self.human_color = human_color

    def reset_match(self) -> None:
        """Start a new match while keeping current menu preferences."""
        self.session.reset()
        self.computer_player = ComputerPlayer(self.selected_rating)
        self.ai_is_thinking = False

    def begin_ai_turn(self) -> None:
        """Mark the AI turn as running."""
        self.ai_is_thinking = True

    def finish_ai_turn(self) -> None:
        """Mark the AI turn as complete."""
        self.ai_is_thinking = False
