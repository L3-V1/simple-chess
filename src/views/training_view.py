from __future__ import annotations

import chess
import pygame

from src.models import OpeningLine, TrainingRuntime

from .board_geometry import BoardGeometry
from .board_view import BoardView
from .layout import (
    build_training_back_button,
    build_training_color_buttons,
    build_training_delete_button,
    build_training_finish_button,
    build_training_library_back_button,
    build_training_moves_input,
    build_training_name_input,
    build_training_save_button,
    build_training_start_button,
)
from .render_assets import RenderAssets
from .text_renderer import UiFont
from .view_models import ActionButton, ColorButton, TextInputField


class TrainingView:
    """Render the opening training library and practice screens."""

    _OPENING_ICON_WIDTH = 34
    _OPENING_TEXT_LEFT = 12 + _OPENING_ICON_WIDTH + 10
    _OPENING_TEXT_RIGHT = 14

    def __init__(self, assets: RenderAssets, geometry: BoardGeometry) -> None:
        self._assets = assets
        self._geometry = geometry
        self._board_view = BoardView(assets, geometry)

    def draw(self, runtime: TrainingRuntime) -> None:
        """Render the full training screen for the current mode."""
        if runtime.practice_session is None:
            self._draw_library(runtime)
            return
        self._draw_practice(runtime)

    def name_input(self) -> TextInputField:
        return build_training_name_input()

    def moves_input(self) -> TextInputField:
        return build_training_moves_input()

    def color_buttons(self) -> list[ColorButton]:
        return build_training_color_buttons()

    def save_opening_button(self) -> ActionButton:
        return build_training_save_button()

    def start_practice_button(self) -> ActionButton:
        return build_training_start_button()

    def delete_opening_button(self) -> ActionButton:
        return build_training_delete_button()

    def library_back_button(self) -> ActionButton:
        return build_training_library_back_button()

    def practice_back_button(self) -> ActionButton:
        return build_training_back_button(self._assets.display_settings)

    def finish_practice_button(self) -> ActionButton:
        return build_training_finish_button(self._assets.display_settings)

    def opening_list_rects(self, openings: list[OpeningLine]) -> list[tuple[OpeningLine, pygame.Rect]]:
        rects: list[tuple[OpeningLine, pygame.Rect]] = []
        left = 470
        top = 190
        width = 340
        height = 52
        gap = 12
        for index, opening in enumerate(openings[:5]):
            rect = pygame.Rect(left, top + index * (height + gap), width, height)
            rects.append((opening, rect))
        return rects

    def practice_board_square(
        self,
        position: tuple[int, int],
        human_color: chess.Color,
    ) -> chess.Square | None:
        return self._geometry.pixel_to_square(position, human_color)

    def practice_promotion_button_at(self, position: tuple[int, int]) -> chess.PieceType | None:
        overlay_rect = self._promotion_overlay_rect()
        if not overlay_rect.collidepoint(position):
            return None
        option_width = overlay_rect.width // 4
        for index, piece_type in enumerate((chess.QUEEN, chess.ROOK, chess.BISHOP, chess.KNIGHT)):
            option_rect = pygame.Rect(
                overlay_rect.left + index * option_width,
                overlay_rect.top + 56,
                option_width,
                overlay_rect.height - 72,
            )
            if option_rect.collidepoint(position):
                return piece_type
        return None

    def _draw_library(self, runtime: TrainingRuntime) -> None:
        self._assets.screen.fill(self._assets.palette.background)
        self._draw_library_header()
        self._draw_form_card(runtime)
        self._draw_openings_card(runtime)

    def _draw_practice(self, runtime: TrainingRuntime) -> None:
        practice = runtime.practice_session
        if practice is None:
            return
        self._assets.screen.fill(self._assets.palette.background)
        self._board_view.draw(practice.session, practice.player_color)
        self._draw_practice_side_panel(runtime)
        if practice.session.pending_promotion is not None:
            self._draw_promotion_overlay(practice.session.board.turn)

    def _draw_library_header(self) -> None:
        title = self._render_text(self._assets.title_font, "Modo Treino de Aberturas", (255, 255, 255))
        subtitle = self._render_text(
            self._assets.body_font,
            "Cadastre linhas e pratique no tabuleiro interativo.",
            (255, 255, 255),
        )
        self._assets.screen.blit(title, title.get_rect(center=(450, 70)))
        self._assets.screen.blit(subtitle, subtitle.get_rect(center=(450, 108)))

    def _draw_form_card(self, runtime: TrainingRuntime) -> None:
        card_rect = pygame.Rect(48, 138, 380, 440)
        self._draw_card(card_rect)
        self._draw_input_field(self.name_input(), runtime.opening_name_input, runtime.active_input == "name")
        self._draw_color_selector(runtime.opening_color)
        self._draw_input_field(self.moves_input(), runtime.opening_moves_input, runtime.active_input == "moves")
        self._draw_button(self.save_opening_button(), self._assets.palette.accent)
        self._draw_button(self.library_back_button(), self._assets.palette.panel)
        if runtime.feedback_message:
            self._draw_wrapped_text(
                text=runtime.feedback_message,
                font=self._assets.small_font,
                color=self._assets.palette.text,
                left=70,
                top=510,
                max_width=320,
                line_height=22,
            )

    def _draw_openings_card(self, runtime: TrainingRuntime) -> None:
        card_rect = pygame.Rect(452, 138, 400, 440)
        self._draw_card(card_rect)
        title = self._render_text(self._assets.body_font, "Aberturas cadastradas")
        self._assets.screen.blit(title, (472, 156))
        for opening, rect in self.opening_list_rects(runtime.openings):
            self._draw_opening_row(
                opening=opening,
                rect=rect,
                is_selected=opening.name == runtime.selected_opening_name,
            )

        if not runtime.openings:
            empty_surface = self._render_text(self._assets.small_font, "Nenhuma abertura cadastrada ainda.")
            self._assets.screen.blit(empty_surface, (472, 220))
        self._draw_button(self.delete_opening_button(), self._assets.palette.danger)
        self._draw_button(self.start_practice_button(), self._assets.palette.accent)

    def _draw_color_selector(self, selected_color: chess.Color) -> None:
        label_surface = self._render_text(self._assets.small_font, "Cor treinada")
        self._assets.screen.blit(label_surface, (70, 220))
        for button in self.color_buttons():
            is_selected = button.color == selected_color
            fill_color = self._assets.palette.accent if is_selected else self._assets.palette.panel
            pygame.draw.rect(self._assets.screen, fill_color, button.rect, border_radius=10)
            pygame.draw.rect(self._assets.screen, self._assets.palette.light_square, button.rect, width=2, border_radius=10)
            label = "Brancas" if button.color == chess.WHITE else "Pretas"
            label_surface = self._render_text(self._assets.small_font, label)
            label_rect = pygame.Rect(button.rect.left + 36, button.rect.top, button.rect.width - 46, button.rect.height)
            if is_selected:
                self._draw_selected_color_icon(button)
            self._assets.screen.blit(label_surface, label_surface.get_rect(center=label_rect.center))

    def _draw_selected_color_icon(self, button: ColorButton) -> None:
        marker_piece = chess.Piece(chess.PAWN, button.color)
        marker_surface = pygame.transform.smoothscale(
            self._assets.piece_factory.get_sprite(marker_piece),
            (24, 24),
        )
        marker_rect = marker_surface.get_rect(midleft=(button.rect.left + 10, button.rect.centery))
        self._assets.screen.blit(marker_surface, marker_rect)

    def _draw_opening_row(
        self,
        opening: OpeningLine,
        rect: pygame.Rect,
        is_selected: bool,
    ) -> None:
        fill_color = self._assets.palette.accent if is_selected else self._assets.palette.panel
        pygame.draw.rect(self._assets.screen, fill_color, rect, border_radius=12)
        pygame.draw.rect(self._assets.screen, self._assets.palette.light_square, rect, width=2, border_radius=12)
        if is_selected:
            self._draw_selected_opening_icon(rect)
        text_width = rect.width - self._OPENING_TEXT_LEFT - self._OPENING_TEXT_RIGHT
        name_surface = self._render_text(
            self._assets.small_font,
            self._fitted_opening_text(opening.name, text_width),
        )
        info_surface = self._render_text(
            self._assets.small_font,
            self._fitted_opening_text(f"{opening.color_label}: {opening.format_moves()}", text_width),
        )
        self._assets.screen.blit(name_surface, (rect.left + self._OPENING_TEXT_LEFT, rect.top + 8))
        self._assets.screen.blit(info_surface, (rect.left + self._OPENING_TEXT_LEFT, rect.top + 28))

    def _draw_selected_opening_icon(self, rect: pygame.Rect) -> None:
        icon_rect = pygame.Rect(rect.left + 12, rect.top + 10, self._OPENING_ICON_WIDTH, 30)
        left_page = pygame.Rect(icon_rect.left + 2, icon_rect.top + 3, 14, 22)
        right_page = pygame.Rect(icon_rect.left + 16, icon_rect.top + 3, 14, 22)
        page_color = (247, 239, 214)
        outline_color = (96, 65, 38)

        pygame.draw.rect(self._assets.screen, page_color, left_page, border_radius=4)
        pygame.draw.rect(self._assets.screen, page_color, right_page, border_radius=4)
        pygame.draw.rect(self._assets.screen, outline_color, left_page, width=2, border_radius=4)
        pygame.draw.rect(self._assets.screen, outline_color, right_page, width=2, border_radius=4)
        pygame.draw.line(
            self._assets.screen,
            outline_color,
            (icon_rect.centerx, icon_rect.top + 4),
            (icon_rect.centerx, icon_rect.bottom - 4),
            2,
        )
        pygame.draw.line(
            self._assets.screen,
            outline_color,
            (left_page.left + 4, left_page.top + 8),
            (left_page.right - 4, left_page.top + 8),
            2,
        )
        pygame.draw.line(
            self._assets.screen,
            outline_color,
            (right_page.left + 4, right_page.top + 8),
            (right_page.right - 4, right_page.top + 8),
            2,
        )

    def _draw_input_field(self, field: TextInputField, value: str, is_active: bool) -> None:
        label_surface = self._render_text(self._assets.small_font, field.label)
        self._assets.screen.blit(label_surface, (field.rect.left, field.rect.top - 26))
        fill_color = (255, 255, 255) if is_active else self._assets.palette.panel
        pygame.draw.rect(self._assets.screen, fill_color, field.rect, border_radius=10)
        pygame.draw.rect(self._assets.screen, self._assets.palette.light_square, field.rect, width=2, border_radius=10)
        if value:
            self._draw_wrapped_text(
                text=value,
                font=self._assets.small_font,
                color=self._assets.palette.text,
                left=field.rect.left + 10,
                top=field.rect.top + 10,
                max_width=field.rect.width - 20,
                line_height=22,
            )
            return
        placeholder = self._render_text(self._assets.small_font, field.placeholder, (120, 140, 128))
        self._assets.screen.blit(placeholder, (field.rect.left + 10, field.rect.top + 10))

    def _fitted_opening_text(self, text: str, max_width: int) -> str:
        return self._assets.text_renderer.fit_to_width(self._assets.small_font, text, max_width)

    def _draw_practice_side_panel(self, runtime: TrainingRuntime) -> None:
        practice = runtime.practice_session
        if practice is None:
            return
        panel_rect = pygame.Rect(
            self._assets.display_settings.board_size,
            0,
            self._assets.display_settings.side_panel_width,
            self._assets.display_settings.window_height,
        )
        pygame.draw.rect(self._assets.screen, self._assets.palette.panel, panel_rect)

        left = self._assets.display_settings.board_size + 22
        top = 24
        title = self._render_text(self._assets.title_font, "Treino")
        opening_name = self._render_text(self._assets.body_font, practice.opening.name)
        color_line = self._render_text(
            self._assets.small_font,
            f"Lado treinado: {practice.opening.color_label}",
        )
        self._assets.screen.blit(title, (left, top))
        self._assets.screen.blit(opening_name, (left, top + 46))
        self._assets.screen.blit(color_line, (left, top + 84))

        top = self._draw_wrapped_text(
            text=practice.instruction_message(),
            font=self._assets.small_font,
            color=self._assets.palette.text,
            left=left,
            top=136,
            max_width=self._assets.display_settings.side_panel_width - 44,
            line_height=24,
        ) + 10
        if practice.session.move_error_message:
            top = self._draw_wrapped_text(
                text=practice.session.move_error_message,
                font=self._assets.small_font,
                color=self._assets.palette.danger,
                left=left,
                top=top,
                max_width=self._assets.display_settings.side_panel_width - 44,
                line_height=23,
            ) + 10

        sequence_title = self._render_text(self._assets.small_font, "Linha cadastrada")
        self._assets.screen.blit(sequence_title, (left, top))
        self._draw_wrapped_text(
            text=practice.opening.format_moves(),
            font=self._assets.small_font,
            color=self._assets.palette.text,
            left=left,
            top=top + 28,
            max_width=self._assets.display_settings.side_panel_width - 44,
            line_height=22,
        )
        self._draw_button(self.finish_practice_button(), self._assets.palette.accent)
        self._draw_button(self.practice_back_button(), self._assets.palette.panel)

    def _draw_promotion_overlay(self, turn_color: chess.Color) -> None:
        shadow = pygame.Surface(
            (self._assets.display_settings.window_width, self._assets.display_settings.window_height),
            pygame.SRCALPHA,
        )
        shadow.fill((0, 0, 0, 120))
        self._assets.screen.blit(shadow, (0, 0))

        overlay_rect = self._promotion_overlay_rect()
        pygame.draw.rect(self._assets.screen, self._assets.palette.panel, overlay_rect, border_radius=14)
        pygame.draw.rect(self._assets.screen, self._assets.palette.text, overlay_rect, width=2, border_radius=14)
        title = self._render_text(self._assets.body_font, "Escolha a promoção")
        self._assets.screen.blit(title, title.get_rect(center=(overlay_rect.centerx, overlay_rect.top + 28)))

        option_width = overlay_rect.width // 4
        for index, piece_type in enumerate((chess.QUEEN, chess.ROOK, chess.BISHOP, chess.KNIGHT)):
            option_rect = pygame.Rect(
                overlay_rect.left + index * option_width,
                overlay_rect.top + 56,
                option_width,
                overlay_rect.height - 72,
            )
            pygame.draw.rect(
                self._assets.screen,
                self._assets.palette.background,
                option_rect.inflate(-8, -8),
                border_radius=10,
            )
            piece = chess.Piece(piece_type, turn_color)
            sprite = self._assets.piece_factory.get_sprite(piece)
            sprite_rect = sprite.get_rect(center=option_rect.center)
            self._assets.screen.blit(sprite, sprite_rect)

    def _promotion_overlay_rect(self) -> pygame.Rect:
        width = 420
        height = 180
        left = (self._assets.display_settings.window_width - width) // 2
        top = (self._assets.display_settings.window_height - height) // 2
        return pygame.Rect(left, top, width, height)

    def _draw_card(self, rect: pygame.Rect) -> None:
        pygame.draw.rect(self._assets.screen, self._assets.palette.panel, rect, border_radius=18)
        pygame.draw.rect(self._assets.screen, self._assets.palette.light_square, rect, width=3, border_radius=18)

    def _draw_button(self, button: ActionButton, fill_color: tuple[int, int, int]) -> None:
        pygame.draw.rect(self._assets.screen, fill_color, button.rect, border_radius=12)
        pygame.draw.rect(self._assets.screen, self._assets.palette.light_square, button.rect, width=2, border_radius=12)
        label_surface = self._render_text(self._assets.small_font, button.label)
        self._assets.screen.blit(label_surface, label_surface.get_rect(center=button.rect.center))

    def _draw_wrapped_text(
        self,
        text: str,
        font: UiFont,
        color: tuple[int, int, int],
        left: int,
        top: int,
        max_width: int,
        line_height: int,
    ) -> int:
        return self._assets.text_renderer.wrap(
            surface=self._assets.screen,
            font=font,
            text=text,
            color=color,
            left=left,
            top=top,
            max_width=max_width,
            line_height=line_height,
        )

    def _render_text(
        self,
        font: UiFont,
        text: str,
        color: tuple[int, int, int] | None = None,
    ) -> pygame.Surface:
        return self._assets.text_renderer.render(font, text, color)
