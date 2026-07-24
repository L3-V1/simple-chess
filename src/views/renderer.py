from __future__ import annotations

import chess
import pygame

from src.core import COLOR_PALETTE, DISPLAY_SETTINGS, EloRating
from src.models import GameSession, TrainingRuntime

from .board_geometry import BoardGeometry
from .game_view import GameView
from .menu_view import MenuView
from .move_history import format_move_history
from .piece_factory import PieceSpriteFactory
from .render_assets import RenderAssets
from .text_renderer import TextRenderer
from .training_view import TrainingView
from .view_models import ActionButton, ColorButton, RatingSlider, TextInputField


class ChessRenderer:
    def __init__(self) -> None:
        square_size = DISPLAY_SETTINGS.square_size
        screen = pygame.display.set_mode((DISPLAY_SETTINGS.window_width, DISPLAY_SETTINGS.window_height))
        pygame.display.set_caption("Xadrez Simples")
        text_renderer = TextRenderer(default_color=COLOR_PALETTE.text)
        piece_factory = PieceSpriteFactory(square_size)
        self.clock = pygame.time.Clock()
        self._assets = RenderAssets(
            screen=screen,
            display_settings=DISPLAY_SETTINGS,
            palette=COLOR_PALETTE,
            square_size=square_size,
            piece_factory=piece_factory,
            text_renderer=text_renderer,
            title_font=text_renderer.title_font,
            body_font=text_renderer.body_font,
            small_font=text_renderer.small_font,
        )
        self._geometry = BoardGeometry(square_size, DISPLAY_SETTINGS.board_size)
        self._menu_view = MenuView(self._assets)
        self._game_view = GameView(self._assets, self._geometry)
        self._training_view = TrainingView(self._assets, self._geometry)

    def draw(
        self,
        session: GameSession,
        selected_rating: EloRating,
        human_color: chess.Color,
        ai_is_thinking: bool,
    ) -> None:
        self._game_view.draw(session, selected_rating, human_color, ai_is_thinking)
        pygame.display.flip()
        self.clock.tick(self._assets.display_settings.fps)

    def draw_menu(self, selected_rating: EloRating, selected_color: chess.Color) -> None:
        self._menu_view.draw(selected_rating, selected_color)
        pygame.display.flip()
        self.clock.tick(self._assets.display_settings.fps)

    def draw_training(self, runtime: TrainingRuntime) -> None:
        self._training_view.draw(runtime)
        pygame.display.flip()
        self.clock.tick(self._assets.display_settings.fps)

    def pixel_to_square(self, position: tuple[int, int], human_color: chess.Color) -> chess.Square | None:
        return self._game_view.pixel_to_square(position, human_color)

    def promotion_button_at(self, position: tuple[int, int]) -> chess.PieceType | None:
        return self._game_view.promotion_button_at(position)

    def rating_slider(self) -> RatingSlider:
        return self._menu_view.rating_slider()

    def menu_start_button(self) -> ActionButton:
        return self._menu_view.menu_start_button()

    def menu_training_button(self) -> ActionButton:
        return self._menu_view.menu_training_button()

    def rating_from_slider_position(self, position: tuple[int, int]) -> EloRating | None:
        return self._menu_view.rating_from_slider_position(position)

    def color_buttons(self) -> list[ColorButton]:
        return self._menu_view.color_buttons()

    def primary_action_button(self, session: GameSession) -> ActionButton:
        return self._game_view.primary_action_button(session)

    def game_save_opening_button(self) -> ActionButton:
        return self._game_view.save_opening_button()

    def training_name_input(self) -> TextInputField:
        return self._training_view.name_input()

    def training_moves_input(self) -> TextInputField:
        return self._training_view.moves_input()

    def training_color_buttons(self) -> list[ColorButton]:
        return self._training_view.color_buttons()

    def training_save_opening_button(self) -> ActionButton:
        return self._training_view.save_opening_button()

    def training_start_button(self) -> ActionButton:
        return self._training_view.start_practice_button()

    def training_delete_button(self) -> ActionButton:
        return self._training_view.delete_opening_button()

    def training_rename_button(self) -> ActionButton:
        return self._training_view.rename_opening_button()

    def training_library_back_button(self) -> ActionButton:
        return self._training_view.library_back_button()

    def training_finish_button(self) -> ActionButton:
        return self._training_view.finish_practice_button()

    def training_practice_back_button(self) -> ActionButton:
        return self._training_view.practice_back_button()

    def training_opening_rows(self, runtime: TrainingRuntime) -> list[tuple[object, pygame.Rect]]:
        return self._training_view.opening_list_rects(runtime.openings)

    def training_pixel_to_square(self, position: tuple[int, int], human_color: chess.Color) -> chess.Square | None:
        return self._training_view.practice_board_square(position, human_color)

    def training_promotion_button_at(self, position: tuple[int, int]) -> chess.PieceType | None:
        return self._training_view.practice_promotion_button_at(position)

    def _format_move_history(self, session: GameSession) -> list[str]:
        return format_move_history(session)
