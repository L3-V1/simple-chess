from __future__ import annotations

from dataclasses import dataclass
from functools import cached_property

import chess


@dataclass(frozen=True)
class OpeningLine:
    """Represent a persisted opening line available for training."""

    name: str
    player_color: chess.Color
    moves_uci: tuple[str, ...]

    @property
    def color_label(self) -> str:
        """Return the localized label for the player color."""
        return "Brancas" if self.player_color == chess.WHITE else "Pretas"

    def to_dict(self) -> dict[str, object]:
        """Serialize the opening line for JSON persistence."""
        return {
            "name": self.name,
            "player_color": "white" if self.player_color == chess.WHITE else "black",
            "moves_uci": list(self.moves_uci),
        }

    @classmethod
    def from_dict(cls, data: dict[str, object]) -> "OpeningLine":
        """Build an opening line from persisted JSON data."""
        player_color = chess.WHITE if data["player_color"] == "white" else chess.BLACK
        return cls(
            name=str(data["name"]),
            player_color=player_color,
            moves_uci=tuple(str(move) for move in data["moves_uci"]),
        )

    def format_moves(self) -> str:
        """Return the opening moves formatted in SAN notation."""
        return self.formatted_moves

    @cached_property
    def formatted_moves(self) -> str:
        """Cache the SAN representation to avoid recomputing it every frame."""
        board = chess.Board()
        san_moves: list[str] = []
        for move_uci in self.moves_uci:
            move = chess.Move.from_uci(move_uci)
            san_moves.append(board.san(move))
            board.push(move)
        return " ".join(san_moves)
