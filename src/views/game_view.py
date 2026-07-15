from __future__ import annotations

import chess
import pygame

from src.core import EloRating
from src.models import GameSession, PROMOTION_PIECES

from .board_geometry import BoardGeometry
from .board_view import BoardView
from .layout import build_primary_action_button
from .move_history import format_move_history
from .render_assets import RenderAssets
from .text_renderer import UiFont
from .view_models import ActionButton


class GameView:
    """Render and handle geometry for the game screen."""

    def __init__(self, assets: RenderAssets, geometry: BoardGeometry) -> None:
        self._assets = assets
        self._geometry = geometry
        self._board_view = BoardView(assets, geometry)

    def draw(
        self,
        session: GameSession,
        selected_rating: EloRating,
        human_color: chess.Color,
        ai_is_thinking: bool,
    ) -> None:
        """Render the full game screen."""
        self._assets.screen.fill(self._assets.palette.background)
        self._board_view.draw(session, human_color)
        self._draw_side_panel(session, selected_rating, human_color, ai_is_thinking)
        if session.pending_promotion is not None:
            self._draw_promotion_overlay(session.board.turn)

    def pixel_to_square(
        self,
        position: tuple[int, int],
        human_color: chess.Color,
    ) -> chess.Square | None:
        return self._geometry.pixel_to_square(position, human_color)

    def promotion_button_at(self, position: tuple[int, int]) -> chess.PieceType | None:
        overlay_rect = self._promotion_overlay_rect()
        if not overlay_rect.collidepoint(position):
            return None

        option_width = overlay_rect.width // len(PROMOTION_PIECES)
        for index, piece_type in enumerate(PROMOTION_PIECES):
            option_rect = pygame.Rect(
                overlay_rect.left + (index * option_width),
                overlay_rect.top + 56,
                option_width,
                overlay_rect.height - 72,
            )
            if option_rect.collidepoint(position):
                return piece_type
        return None

    def primary_action_button(self, session: GameSession) -> ActionButton:
        return build_primary_action_button(
            display_settings=self._assets.display_settings,
            board_size=self._assets.display_settings.board_size,
            is_finished=session.is_finished(),
        )

    def _draw_side_panel(
        self,
        session: GameSession,
        selected_rating: EloRating,
        human_color: chess.Color,
        ai_is_thinking: bool,
    ) -> None:
        self._draw_panel_background()
        left = self._assets.display_settings.board_size + 22
        top = self._draw_panel_header(left, selected_rating, human_color, ai_is_thinking)
        top = self._draw_panel_messages(session, left, top)
        self._draw_move_history(session, left, top + 6)
        self._draw_action_button(
            self.primary_action_button(session),
            self._assets.palette.accent if session.is_finished() else self._assets.palette.danger,
        )

    def _draw_panel_background(self) -> None:
        panel_rect = pygame.Rect(
            self._assets.display_settings.board_size,
            0,
            self._assets.display_settings.side_panel_width,
            self._assets.display_settings.window_height,
        )
        pygame.draw.rect(self._assets.screen, self._assets.palette.panel, panel_rect)

    def _draw_panel_header(
        self,
        left: int,
        selected_rating: EloRating,
        human_color: chess.Color,
        ai_is_thinking: bool,
    ) -> int:
        top = 24
        header_lines = [
            ("Xadrez Simples", self._assets.title_font),
            (f"Rating IA: {selected_rating.label}", self._assets.body_font),
            (f"Humano: {'Brancas' if human_color == chess.WHITE else 'Pretas'}", self._assets.body_font),
            (f"IA: {'Pensando...' if ai_is_thinking else 'Aguardando'}", self._assets.body_font),
        ]
        for line, font in header_lines:
            text_surface = self._render_text(font, line)
            self._assets.screen.blit(text_surface, (left, top))
            top += 46
        return top

    def _draw_panel_messages(self, session: GameSession, left: int, top: int) -> int:
        top = self._draw_wrapped_text(
            text=session.status_message(),
            font=self._assets.body_font,
            color=self._assets.palette.text,
            left=left,
            top=top,
            max_width=self._assets.display_settings.side_panel_width - 44,
            line_height=28,
        ) + 10
        if session.move_error_message:
            top = self._draw_wrapped_text(
                text=session.move_error_message,
                font=self._assets.small_font,
                color=self._assets.palette.danger,
                left=left,
                top=top,
                max_width=self._assets.display_settings.side_panel_width - 44,
                line_height=23,
            ) + 10
        return top

    def _draw_move_history(self, session: GameSession, left: int, top: int) -> None:
        title = self._render_text(self._assets.body_font, "Histórico")
        self._assets.screen.blit(title, (left, top))
        move_stack = format_move_history(session)

        for index in range(0, len(move_stack), 2):
            move_number = (len(session.board.move_stack[: index + 1]) + 1) // 2
            white_move = move_stack[index]
            black_move = move_stack[index + 1] if index + 1 < len(move_stack) else ""
            row_surface = self._render_text(
                self._assets.small_font,
                f"{move_number}. {white_move} {black_move}".strip(),
            )
            self._assets.screen.blit(row_surface, (left, top + 34 + (index // 2) * 24))

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

        option_width = overlay_rect.width // len(PROMOTION_PIECES)
        for index, piece_type in enumerate(PROMOTION_PIECES):
            option_rect = pygame.Rect(
                overlay_rect.left + (index * option_width),
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
