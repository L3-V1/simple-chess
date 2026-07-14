from __future__ import annotations

import chess
import pygame

from src.core import DisplaySettings
from src.views.view_models import ActionButton, ColorButton, RatingSlider


def build_rating_slider(display_settings: DisplaySettings) -> RatingSlider:
    """Create the rating slider geometry used by the menu."""
    return RatingSlider(
        rect=pygame.Rect(200, 338, 500, 18),
        knob_radius=14,
    )


def build_menu_start_button() -> ActionButton:
    """Create the main menu action button."""
    return ActionButton(
        label="Iniciar partida",
        rect=pygame.Rect(310, 470, 280, 52),
    )


def build_color_buttons(display_settings: DisplaySettings) -> list[ColorButton]:
    """Create the color selection buttons for the main menu."""
    buttons: list[ColorButton] = []
    top = 234
    width = 190
    height = 42
    gap = 18
    left = (display_settings.window_width - ((width * 2) + gap)) // 2
    for index, color in enumerate((chess.WHITE, chess.BLACK)):
        rect = pygame.Rect(left + index * (width + gap), top, width, height)
        buttons.append(ColorButton(color=color, rect=rect))
    return buttons


def build_primary_action_button(
    display_settings: DisplaySettings,
    board_size: int,
    is_finished: bool,
) -> ActionButton:
    """Create the in-game primary action button."""
    label = "Nova partida" if is_finished else "Abandonar partida"
    rect = pygame.Rect(
        board_size + 22,
        display_settings.window_height - 76,
        display_settings.side_panel_width - 44,
        46,
    )
    return ActionButton(label=label, rect=rect)
