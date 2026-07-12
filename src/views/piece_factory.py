from __future__ import annotations

from pathlib import Path

import chess
import pygame

PIECE_FILENAMES = {
    (chess.WHITE, chess.KING): "wK.svg",
    (chess.WHITE, chess.QUEEN): "wQ.svg",
    (chess.WHITE, chess.ROOK): "wR.svg",
    (chess.WHITE, chess.BISHOP): "wB.svg",
    (chess.WHITE, chess.KNIGHT): "wN.svg",
    (chess.WHITE, chess.PAWN): "wP.svg",
    (chess.BLACK, chess.KING): "bK.svg",
    (chess.BLACK, chess.QUEEN): "bQ.svg",
    (chess.BLACK, chess.ROOK): "bR.svg",
    (chess.BLACK, chess.BISHOP): "bB.svg",
    (chess.BLACK, chess.KNIGHT): "bN.svg",
    (chess.BLACK, chess.PAWN): "bP.svg",
}


class PieceSpriteFactory:
    def __init__(self, square_size: int) -> None:
        self._square_size = square_size
        self._target_size = int(square_size * 0.86)
        self._asset_directory = (
            Path(__file__).resolve().parent.parent.parent / "assets" / "piece_sets" / "chessnut"
        )
        self._cache: dict[tuple[chess.Color, chess.PieceType], pygame.Surface] = {}

    def get_sprite(self, piece: chess.Piece) -> pygame.Surface:
        key = (piece.color, piece.piece_type)
        sprite = self._cache.get(key)
        if sprite is None:
            sprite = self._build_sprite(piece)
            self._cache[key] = sprite
        return sprite

    def _build_sprite(self, piece: chess.Piece) -> pygame.Surface:
        filename = PIECE_FILENAMES[(piece.color, piece.piece_type)]
        asset_path = self._asset_directory / filename
        if not asset_path.exists():
            raise FileNotFoundError(f"Piece asset not found: {asset_path}")

        loaded_surface = pygame.image.load(str(asset_path))
        if pygame.display.get_surface() is not None:
            loaded_surface = loaded_surface.convert_alpha()
        loaded_surface = self._trim_transparent_margins(loaded_surface)
        scaled_surface = pygame.transform.smoothscale(
            loaded_surface,
            (self._target_size, self._target_size),
        )

        surface = pygame.Surface((self._square_size, self._square_size), pygame.SRCALPHA)
        rect = scaled_surface.get_rect(center=(self._square_size // 2, self._square_size // 2))
        surface.blit(scaled_surface, rect)
        return surface

    def _trim_transparent_margins(self, surface: pygame.Surface) -> pygame.Surface:
        bounding_rect = surface.get_bounding_rect(min_alpha=1)
        if bounding_rect.width == 0 or bounding_rect.height == 0:
            return surface
        return surface.subsurface(bounding_rect).copy()
