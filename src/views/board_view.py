from __future__ import annotations

import chess
import pygame

from src.models import GameSession

from .board_geometry import BoardGeometry
from .render_assets import RenderAssets
from .text_renderer import UiFont


class BoardView:
    """Render a chess board independently from any screen-specific side panel."""

    def __init__(self, assets: RenderAssets, geometry: BoardGeometry) -> None:
        self._assets = assets
        self._geometry = geometry

    def draw(self, session: GameSession, human_color: chess.Color) -> None:
        """Render the board, pieces, highlights and coordinates."""
        for display_rank in range(8):
            for display_file in range(8):
                square = self._geometry.square_from_display(display_file, display_rank, human_color)
                self._draw_square_background(square, display_rank, display_file, session, human_color)
                piece = session.board.piece_at(square)
                if piece is not None:
                    self._draw_piece(display_file, display_rank, piece)
        self._draw_coordinates(human_color)

    def _draw_square_background(
        self,
        square: chess.Square,
        display_rank: int,
        display_file: int,
        session: GameSession,
        human_color: chess.Color,
    ) -> None:
        base_color = (
            self._assets.palette.light_square
            if (display_rank + display_file) % 2 == 0
            else self._assets.palette.dark_square
        )
        rect = pygame.Rect(
            display_file * self._assets.square_size,
            display_rank * self._assets.square_size,
            self._assets.square_size,
            self._assets.square_size,
        )
        pygame.draw.rect(self._assets.screen, base_color, rect)

        if session.selected_square == square:
            pygame.draw.rect(self._assets.screen, self._assets.palette.highlight, rect, width=5)
        if session.last_move and square in (session.last_move.from_square, session.last_move.to_square):
            pygame.draw.rect(self._assets.screen, self._assets.palette.accent, rect, width=4)
        if square in session.legal_targets:
            is_capture = session.board.piece_at(square) is not None
            self._draw_legal_move_hint(square, is_capture, human_color)

    def _draw_legal_move_hint(self, square: chess.Square, is_capture: bool, human_color: chess.Color) -> None:
        display_file, display_rank = self._geometry.display_from_square(square, human_color)
        center_x = display_file * self._assets.square_size + (self._assets.square_size // 2)
        center_y = display_rank * self._assets.square_size + (self._assets.square_size // 2)
        color = self._assets.palette.capture_move if is_capture else self._assets.palette.legal_move
        radius = self._assets.square_size // 7 if not is_capture else self._assets.square_size // 2 - 8
        width = 0 if not is_capture else 5
        pygame.draw.circle(self._assets.screen, color, (center_x, center_y), radius, width=width)

    def _draw_piece(self, display_file: int, display_rank: int, piece: chess.Piece) -> None:
        rect = pygame.Rect(
            display_file * self._assets.square_size,
            display_rank * self._assets.square_size,
            self._assets.square_size,
            self._assets.square_size,
        )
        self._assets.screen.blit(self._assets.piece_factory.get_sprite(piece), rect)

    def _draw_coordinates(self, human_color: chess.Color) -> None:
        for display_file in range(8):
            file_index = display_file if human_color == chess.WHITE else 7 - display_file
            file_surface = self._render_text(self._assets.small_font, chr(ord("a") + file_index))
            self._assets.screen.blit(
                file_surface,
                (display_file * self._assets.square_size + 6, self._assets.display_settings.board_size - 22),
            )

        for display_rank in range(8):
            rank_value = 8 - display_rank if human_color == chess.WHITE else display_rank + 1
            rank_surface = self._render_text(self._assets.small_font, str(rank_value))
            self._assets.screen.blit(rank_surface, (6, display_rank * self._assets.square_size + 6))

    def _render_text(
        self,
        font: UiFont,
        text: str,
        color: tuple[int, int, int] | None = None,
    ) -> pygame.Surface:
        return self._assets.text_renderer.render(font, text, color)
