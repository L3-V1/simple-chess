"""View layer components."""

from src.views.board_geometry import BoardGeometry
from src.views.board_view import BoardView
from src.views.game_view import GameView
from src.views.layout import (
    build_color_buttons,
    build_menu_start_button,
    build_menu_training_button,
    build_primary_action_button,
    build_rating_slider,
    build_save_opening_button,
    build_training_rename_button,
)
from src.views.menu_view import MenuView
from src.views.move_history import format_move_history, normalize_move_notation
from src.views.piece_factory import PieceSpriteFactory
from src.views.render_assets import RenderAssets
from src.views.renderer import ChessRenderer
from src.views.text_renderer import TextRenderer
from src.views.training_view import TrainingView
from src.views.view_models import ActionButton, ColorButton, RatingSlider, TextInputField

__all__ = [
    "ActionButton",
    "BoardGeometry",
    "BoardView",
    "ChessRenderer",
    "ColorButton",
    "GameView",
    "MenuView",
    "PieceSpriteFactory",
    "RenderAssets",
    "RatingSlider",
    "TextRenderer",
    "TextInputField",
    "TrainingView",
    "build_color_buttons",
    "build_menu_start_button",
    "build_menu_training_button",
    "build_primary_action_button",
    "build_rating_slider",
    "build_save_opening_button",
    "build_training_rename_button",
    "format_move_history",
    "normalize_move_notation",
]
