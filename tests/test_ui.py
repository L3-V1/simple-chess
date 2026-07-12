import chess
import pygame

from core import EloRating
from models import GameSession
from views import PieceSpriteFactory
from views.renderer import ChessRenderer


def test_piece_sprite_factory_loads_default_piece_set() -> None:
    pygame.init()
    try:
        factory = PieceSpriteFactory(square_size=80)

        sprite = factory.get_sprite(chess.Piece(chess.QUEEN, chess.WHITE))

        assert sprite.get_size() == (80, 80)
        assert sprite.get_bounding_rect(min_alpha=1).width > 0
        assert sprite.get_bounding_rect(min_alpha=1).height > 0
    finally:
        pygame.quit()


def test_renderer_formats_move_history_with_short_piece_notation() -> None:
    pygame.init()
    try:
        renderer = ChessRenderer()
        session = GameSession()
        session.board.push_san("e4")
        session.board.push_san("e5")
        session.board.push_san("Nf3")

        move_history = renderer._format_move_history(session)

        assert move_history == ["e4", "e5", "Nf3"]
    finally:
        pygame.quit()


def test_renderer_slider_snaps_to_supported_elo_values() -> None:
    pygame.init()
    try:
        renderer = ChessRenderer()
        slider = renderer.rating_slider()

        left_rating = renderer.rating_from_slider_position((slider.rect.left, slider.rect.centery))
        middle_rating = renderer.rating_from_slider_position((slider.rect.centerx, slider.rect.centery))
        right_rating = renderer.rating_from_slider_position((slider.rect.right, slider.rect.centery))

        assert left_rating == EloRating.ELO_500
        assert middle_rating == EloRating.ELO_1500
        assert right_rating == EloRating.ELO_2500
    finally:
        pygame.quit()
