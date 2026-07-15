from __future__ import annotations

import chess


class BoardGeometry:
    """Convert between board coordinates and screen coordinates."""

    def __init__(self, square_size: int, board_size: int) -> None:
        self._square_size = square_size
        self._board_size = board_size

    def pixel_to_square(
        self,
        position: tuple[int, int],
        human_color: chess.Color,
    ) -> chess.Square | None:
        """Translate a mouse position into a board square when inside the board."""
        x_position, y_position = position
        if x_position >= self._board_size or y_position >= self._board_size:
            return None
        display_file = x_position // self._square_size
        display_rank = y_position // self._square_size
        return self.square_from_display(display_file, display_rank, human_color)

    def square_from_display(
        self,
        display_file: int,
        display_rank: int,
        human_color: chess.Color,
    ) -> chess.Square:
        """Translate display coordinates into a chess square."""
        if human_color == chess.WHITE:
            return chess.square(display_file, 7 - display_rank)
        return chess.square(7 - display_file, display_rank)

    def display_from_square(
        self,
        square: chess.Square,
        human_color: chess.Color,
    ) -> tuple[int, int]:
        """Translate a chess square into display coordinates."""
        file_index = chess.square_file(square)
        rank_index = chess.square_rank(square)
        if human_color == chess.WHITE:
            return file_index, 7 - rank_index
        return 7 - file_index, rank_index
