import chess

from src.core import EloRating
from src.models import GameRuntime


def test_game_runtime_updates_menu_preferences() -> None:
    runtime = GameRuntime()

    runtime.apply_menu_selection(EloRating.ELO_2000, chess.BLACK)

    assert runtime.selected_rating == EloRating.ELO_2000
    assert runtime.human_color == chess.BLACK
    assert runtime.computer_player.rating == EloRating.ELO_1500


def test_game_runtime_reset_match_rebuilds_player_with_current_rating() -> None:
    runtime = GameRuntime()
    runtime.apply_menu_selection(EloRating.ELO_2500, chess.BLACK)
    runtime.session.resign(chess.WHITE)

    runtime.reset_match()

    assert runtime.session.is_finished() is False
    assert runtime.computer_player.rating == EloRating.ELO_2500
    assert runtime.ai_is_thinking is False
