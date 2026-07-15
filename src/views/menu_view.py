from __future__ import annotations

import chess
import pygame

from src.core import ELO_RATINGS, EloRating

from .layout import (
    build_color_buttons,
    build_menu_start_button,
    build_menu_training_button,
    build_rating_slider,
)
from .render_assets import RenderAssets
from .text_renderer import UiFont
from .view_models import ActionButton, ColorButton, RatingSlider


class MenuView:
    """Render and handle geometry for the main menu screen."""

    def __init__(self, assets: RenderAssets) -> None:
        self._assets = assets

    def draw(self, selected_rating: EloRating, selected_color: chess.Color) -> None:
        """Render the full menu screen."""
        self._draw_background()
        self._draw_header()
        self._draw_color_section(selected_color)
        self._draw_rating_slider(selected_rating)
        self._draw_action_button(self.menu_start_button(), self._assets.palette.accent)
        self._draw_action_button(self.menu_training_button(), self._assets.palette.panel)

    def rating_slider(self) -> RatingSlider:
        return build_rating_slider(self._assets.display_settings)

    def menu_start_button(self) -> ActionButton:
        return build_menu_start_button()

    def menu_training_button(self) -> ActionButton:
        return build_menu_training_button()

    def color_buttons(self) -> list[ColorButton]:
        return build_color_buttons(self._assets.display_settings)

    def rating_from_slider_position(self, position: tuple[int, int]) -> EloRating | None:
        slider = self.rating_slider()
        interaction_rect = slider.rect.inflate(0, 36)
        interaction_rect.left -= slider.knob_radius
        interaction_rect.width += slider.knob_radius * 2
        if not interaction_rect.collidepoint(position):
            return None

        clamped_x = max(slider.rect.left, min(position[0], slider.rect.right))
        if len(ELO_RATINGS) == 1:
            return ELO_RATINGS[0]

        step_width = slider.rect.width / (len(ELO_RATINGS) - 1)
        index = round((clamped_x - slider.rect.left) / step_width)
        return ELO_RATINGS[max(0, min(index, len(ELO_RATINGS) - 1))]

    def _draw_background(self) -> None:
        self._assets.screen.fill(self._assets.palette.background)
        header_rect = pygame.Rect(72, 52, self._assets.display_settings.window_width - 144, 116)
        pygame.draw.rect(self._assets.screen, self._assets.palette.panel, header_rect, border_radius=18)
        pygame.draw.rect(
            self._assets.screen,
            self._assets.palette.light_square,
            header_rect,
            width=3,
            border_radius=18,
        )

        tile_size = 42
        for file_index in range(12):
            color = self._assets.palette.light_square if file_index % 2 == 0 else self._assets.palette.dark_square
            rect = pygame.Rect(198 + file_index * tile_size, 584, tile_size, tile_size)
            pygame.draw.rect(self._assets.screen, color, rect, border_radius=4)

    def _draw_header(self) -> None:
        title_surface = self._render_text(self._assets.title_font, "Escolha o Rating da IA")
        subtitle_surface = self._render_text(
            self._assets.body_font,
            "Selecione sua cor, ajuste o slider e inicie a partida.",
        )
        self._assets.screen.blit(title_surface, title_surface.get_rect(center=(450, 104)))
        self._assets.screen.blit(subtitle_surface, subtitle_surface.get_rect(center=(450, 144)))

    def _draw_color_section(self, selected_color: chess.Color) -> None:
        color_prompt_surface = self._render_text(
            self._assets.body_font,
            "Escolha com quais peças você vai jogar:",
            (255, 255, 255),
        )
        self._assets.screen.blit(color_prompt_surface, color_prompt_surface.get_rect(center=(450, 198)))
        for button in self.color_buttons():
            self._draw_color_button(button, selected_color)

    def _draw_color_button(self, button: ColorButton, selected_color: chess.Color) -> None:
        is_selected = button.color == selected_color
        fill_color = self._assets.palette.accent if is_selected else self._assets.palette.panel
        pygame.draw.rect(self._assets.screen, fill_color, button.rect, border_radius=12)
        pygame.draw.rect(
            self._assets.screen,
            self._assets.palette.light_square,
            button.rect,
            width=2,
            border_radius=12,
        )
        label = "Brancas" if button.color == chess.WHITE else "Pretas"
        label_surface = self._render_text(self._assets.small_font, label)
        label_rect = pygame.Rect(button.rect.left + 40, button.rect.top, button.rect.width - 52, button.rect.height)
        if is_selected:
            self._draw_selected_color_icon(button)
        self._assets.screen.blit(label_surface, label_surface.get_rect(center=label_rect.center))

    def _draw_selected_color_icon(self, button: ColorButton) -> None:
        marker_piece = chess.Piece(chess.PAWN, button.color)
        marker_surface = pygame.transform.smoothscale(
            self._assets.piece_factory.get_sprite(marker_piece),
            (28, 28),
        )
        marker_rect = marker_surface.get_rect(midleft=(button.rect.left + 16, button.rect.centery))
        self._assets.screen.blit(marker_surface, marker_rect)

    def _draw_rating_slider(self, selected_rating: EloRating) -> None:
        slider = self.rating_slider()
        slider_text_color = (255, 255, 255)
        label_surface = self._render_text(
            self._assets.body_font,
            f"Elo selecionado: {selected_rating.label}",
            slider_text_color,
        )
        self._assets.screen.blit(label_surface, label_surface.get_rect(center=(450, slider.rect.top - 28)))
        self._draw_slider_track(slider)
        self._draw_slider_ticks(slider, slider_text_color)
        knob_center = (self._slider_x_for_rating(selected_rating), slider.rect.centery)
        pygame.draw.circle(self._assets.screen, self._assets.palette.accent, knob_center, slider.knob_radius)
        pygame.draw.circle(self._assets.screen, self._assets.palette.text, knob_center, slider.knob_radius, width=2)

    def _draw_slider_track(self, slider: RatingSlider) -> None:
        pygame.draw.line(
            self._assets.screen,
            self._assets.palette.light_square,
            slider.rect.midleft,
            slider.rect.midright,
            width=6,
        )

    def _draw_slider_ticks(self, slider: RatingSlider, text_color: tuple[int, int, int]) -> None:
        for rating in ELO_RATINGS:
            x_position = self._slider_x_for_rating(rating)
            pygame.draw.circle(
                self._assets.screen,
                self._assets.palette.light_square,
                (x_position, slider.rect.centery),
                5,
            )
            tick_label = self._render_text(self._assets.small_font, rating.label, text_color)
            self._assets.screen.blit(
                tick_label,
                tick_label.get_rect(center=(x_position, slider.rect.bottom + 18)),
            )

    def _slider_x_for_rating(self, rating: EloRating) -> int:
        slider = self.rating_slider()
        index = ELO_RATINGS.index(rating)
        if len(ELO_RATINGS) == 1:
            return slider.rect.left
        step_width = slider.rect.width / (len(ELO_RATINGS) - 1)
        return round(slider.rect.left + index * step_width)

    def _draw_action_button(self, button: ActionButton, fill_color: tuple[int, int, int]) -> None:
        pygame.draw.rect(self._assets.screen, fill_color, button.rect, border_radius=12)
        pygame.draw.rect(
            self._assets.screen,
            self._assets.palette.light_square,
            button.rect,
            width=2,
            border_radius=12,
        )
        label_surface = self._render_text(self._assets.small_font, button.label)
        self._assets.screen.blit(label_surface, label_surface.get_rect(center=button.rect.center))

    def _render_text(
        self,
        font: UiFont,
        text: str,
        color: tuple[int, int, int] | None = None,
    ) -> pygame.Surface:
        return self._assets.text_renderer.render(font, text, color)
