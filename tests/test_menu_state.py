import chess

from src.controllers import MenuSelection
from src.core import EloRating


def test_menu_selection_reports_color_changes() -> None:
    selection = MenuSelection(rating=EloRating.ELO_1500, color=chess.WHITE)

    changed = selection.select_color(chess.BLACK)

    assert changed is True
    assert selection.color == chess.BLACK


def test_menu_selection_ignores_same_color_selection() -> None:
    selection = MenuSelection(rating=EloRating.ELO_1500, color=chess.WHITE)

    changed = selection.select_color(chess.WHITE)

    assert changed is False
    assert selection.color == chess.WHITE
