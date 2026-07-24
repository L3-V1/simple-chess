from __future__ import annotations

import chess
import pygame

from src.core import DisplaySettings
from src.views.view_models import ActionButton, ColorButton, RatingSlider, TextInputField


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
        rect=pygame.Rect(310, 450, 280, 48),
    )


def build_menu_training_button() -> ActionButton:
    """Create the training mode entry button."""
    return ActionButton(
        label="Modo Treino",
        rect=pygame.Rect(310, 512, 280, 48),
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


def build_save_opening_button(
    display_settings: DisplaySettings,
    board_size: int,
) -> ActionButton:
    """Create the in-game button that saves the current line for training."""
    return ActionButton(
        label="Salvar para treino",
        rect=pygame.Rect(
            board_size + 22,
            display_settings.window_height - 132,
            display_settings.side_panel_width - 44,
            46,
        ),
    )


def build_training_back_button(display_settings: DisplaySettings) -> ActionButton:
    """Create the button that returns from training to the main menu."""
    left = display_settings.board_size + 22
    return ActionButton(
        label="Voltar ao menu",
        rect=pygame.Rect(left, display_settings.window_height - 76, display_settings.side_panel_width - 44, 46),
    )


def build_training_finish_button(display_settings: DisplaySettings) -> ActionButton:
    """Create the button that exits an active training practice."""
    left = display_settings.board_size + 22
    return ActionButton(
        label="Encerrar treino",
        rect=pygame.Rect(left, display_settings.window_height - 132, display_settings.side_panel_width - 44, 46),
    )


def build_training_name_input() -> TextInputField:
    """Create the name input field geometry for training mode."""
    return TextInputField(
        label="Nome da abertura",
        rect=pygame.Rect(70, 170, 320, 44),
        placeholder="Ex.: Ruy Lopez",
    )


def build_training_moves_input() -> TextInputField:
    """Create the move sequence input field geometry for training mode."""
    return TextInputField(
        label="Lances da linha",
        rect=pygame.Rect(70, 336, 320, 88),
        placeholder="Ex.: 1. e4 e5 2. Nf3 Nc6 3. Bb5 a6",
    )


def build_training_save_button() -> ActionButton:
    """Create the save opening button."""
    return ActionButton(
        label="Salvar abertura",
        rect=pygame.Rect(70, 452, 200, 46),
    )


def build_training_start_button() -> ActionButton:
    """Create the start practice button."""
    return ActionButton(
        label="Praticar abertura",
        rect=pygame.Rect(610, 560, 220, 46),
    )


def build_training_delete_button() -> ActionButton:
    """Create the delete opening button."""
    return ActionButton(
        label="Excluir abertura",
        rect=pygame.Rect(638, 502, 176, 46),
    )


def build_training_rename_button() -> ActionButton:
    """Create the rename opening button."""
    return ActionButton(
        label="Editar nome",
        rect=pygame.Rect(470, 502, 156, 46),
    )


def build_training_library_back_button() -> ActionButton:
    """Create the back button shown in the training library screen."""
    return ActionButton(
        label="Voltar ao menu",
        rect=pygame.Rect(70, 560, 180, 46),
    )


def build_training_color_buttons() -> list[ColorButton]:
    """Create the color selection buttons for opening registration."""
    top = 250
    left = 70
    width = 150
    height = 44
    gap = 18
    return [
        ColorButton(color=chess.WHITE, rect=pygame.Rect(left, top, width, height)),
        ColorButton(color=chess.BLACK, rect=pygame.Rect(left + width + gap, top, width, height)),
    ]
