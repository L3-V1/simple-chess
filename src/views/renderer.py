from __future__ import annotations

import chess
import pygame

from src.core import COLOR_PALETTE, DISPLAY_SETTINGS, ELO_RATINGS, EloRating
from src.models import GameSession, PROMOTION_PIECES
from src.views.layout import (
    build_color_buttons,
    build_menu_start_button,
    build_primary_action_button,
    build_rating_slider,
)
from src.views.move_history import format_move_history
from src.views.piece_factory import PieceSpriteFactory
from src.views.text_renderer import TextRenderer, UiFont
from src.views.view_models import ActionButton, ColorButton, RatingSlider


class ChessRenderer:
    def __init__(self) -> None:
        self.display_settings = DISPLAY_SETTINGS
        self.palette = COLOR_PALETTE
        self.square_size = DISPLAY_SETTINGS.square_size
        self.screen = pygame.display.set_mode(
            (DISPLAY_SETTINGS.window_width, DISPLAY_SETTINGS.window_height)
        )
        pygame.display.set_caption("Xadrez Simples")
        self.clock = pygame.time.Clock()
        self.piece_factory = PieceSpriteFactory(self.square_size)
        self.text_renderer = TextRenderer(default_color=self.palette.text)
        self.title_font = self.text_renderer.title_font
        self.body_font = self.text_renderer.body_font
        self.small_font = self.text_renderer.small_font

    def draw(
        self,
        session: GameSession,
        selected_rating: EloRating,
        human_color: chess.Color,
        ai_is_thinking: bool,
    ) -> None:
        self.screen.fill(self.palette.background)
        self._draw_board(session, human_color)
        self._draw_side_panel(session, selected_rating, human_color, ai_is_thinking)
        if session.pending_promotion is not None:
            self._draw_promotion_overlay(session.board.turn)
        pygame.display.flip()
        self.clock.tick(self.display_settings.fps)

    def draw_menu(self, selected_rating: EloRating, selected_color: chess.Color) -> None:
        self._draw_menu_background()
        title_surface = self._render_text(self.title_font, "Escolha o Rating da IA")
        subtitle_surface = self._render_text(
            self.body_font,
            "Selecione sua cor, ajuste o slider e inicie a partida.",
        )
        self.screen.blit(title_surface, title_surface.get_rect(center=(450, 104)))
        self.screen.blit(subtitle_surface, subtitle_surface.get_rect(center=(450, 144)))
        color_prompt_surface = self._render_text(
            self.body_font,
            "Escolha com quais peças voce vai jogar:",
            (255, 255, 255),
        )
        self.screen.blit(color_prompt_surface, color_prompt_surface.get_rect(center=(450, 198)))

        for button in self.color_buttons():
            self._draw_color_button(button, selected_color)

        self._draw_rating_slider(selected_rating)
        self._draw_action_button(self.menu_start_button(), self.palette.accent)

        pygame.display.flip()
        self.clock.tick(self.display_settings.fps)

    def pixel_to_square(self, position: tuple[int, int], human_color: chess.Color) -> chess.Square | None:
        x_position, y_position = position
        if x_position >= self.display_settings.board_size or y_position >= self.display_settings.board_size:
            return None
        display_file = x_position // self.square_size
        display_rank = y_position // self.square_size
        return self._square_from_display(display_file, display_rank, human_color)

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

    def rating_slider(self) -> RatingSlider:
        return build_rating_slider(self.display_settings)

    def menu_start_button(self) -> ActionButton:
        return build_menu_start_button()

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

    def color_buttons(self) -> list[ColorButton]:
        return build_color_buttons(self.display_settings)

    def primary_action_button(self, session: GameSession) -> ActionButton:
        return build_primary_action_button(
            display_settings=self.display_settings,
            board_size=self.display_settings.board_size,
            is_finished=session.is_finished(),
        )

    def _draw_board(self, session: GameSession, human_color: chess.Color) -> None:
        for display_rank in range(8):
            for display_file in range(8):
                square = self._square_from_display(display_file, display_rank, human_color)
                self._draw_square_background(square, display_rank, display_file, session, human_color)
                piece = session.board.piece_at(square)
                if piece is not None:
                    self._draw_piece(display_file, display_rank, piece)
        self._draw_coordinates(human_color)

    def _draw_square_background(
        self,
        square: chess.Square,
        display_rank: int,
        display_file: int,
        session: GameSession,
        human_color: chess.Color,
    ) -> None:
        base_color = self.palette.light_square if (display_rank + display_file) % 2 == 0 else self.palette.dark_square
        rect = pygame.Rect(
            display_file * self.square_size,
            display_rank * self.square_size,
            self.square_size,
            self.square_size,
        )
        pygame.draw.rect(self.screen, base_color, rect)

        if session.selected_square == square:
            pygame.draw.rect(self.screen, self.palette.highlight, rect, width=5)
        if session.last_move and square in (session.last_move.from_square, session.last_move.to_square):
            pygame.draw.rect(self.screen, self.palette.accent, rect, width=4)
        if square in session.legal_targets:
            self._draw_legal_move_hint(square, session.board.piece_at(square) is not None, human_color)

    def _draw_legal_move_hint(self, square: chess.Square, is_capture: bool, human_color: chess.Color) -> None:
        display_file, display_rank = self._display_from_square(square, human_color)
        center_x = display_file * self.square_size + (self.square_size // 2)
        center_y = display_rank * self.square_size + (self.square_size // 2)
        color = self.palette.capture_move if is_capture else self.palette.legal_move
        radius = self.square_size // 7 if not is_capture else self.square_size // 2 - 8
        width = 0 if not is_capture else 5
        pygame.draw.circle(self.screen, color, (center_x, center_y), radius, width=width)

    def _draw_piece(self, display_file: int, display_rank: int, piece: chess.Piece) -> None:
        rect = pygame.Rect(
            display_file * self.square_size,
            display_rank * self.square_size,
            self.square_size,
            self.square_size,
        )
        self.screen.blit(self.piece_factory.get_sprite(piece), rect)

    def _draw_coordinates(self, human_color: chess.Color) -> None:
        for display_file in range(8):
            file_index = display_file if human_color == chess.WHITE else 7 - display_file
            file_surface = self._render_text(self.small_font, chr(ord("a") + file_index))
            self.screen.blit(
                file_surface,
                (display_file * self.square_size + 6, self.display_settings.board_size - 22),
            )

        for display_rank in range(8):
            rank_value = 8 - display_rank if human_color == chess.WHITE else display_rank + 1
            rank_surface = self._render_text(self.small_font, str(rank_value))
            self.screen.blit(rank_surface, (6, display_rank * self.square_size + 6))

    def _draw_side_panel(
        self,
        session: GameSession,
        selected_rating: EloRating,
        human_color: chess.Color,
        ai_is_thinking: bool,
    ) -> None:
        self._draw_panel_background()
        left = self.display_settings.board_size + 22
        top = self._draw_panel_header(left, selected_rating, human_color, ai_is_thinking)
        top = self._draw_panel_messages(session, left, top)
        self._draw_move_history(session, left, top + 6)
        self._draw_action_button(
            self.primary_action_button(session),
            self.palette.accent if session.is_finished() else self.palette.danger,
        )

    def _draw_panel_background(self) -> None:
        panel_rect = pygame.Rect(
            self.display_settings.board_size,
            0,
            self.display_settings.side_panel_width,
            self.display_settings.window_height,
        )
        pygame.draw.rect(self.screen, self.palette.panel, panel_rect)

    def _draw_panel_header(
        self,
        left: int,
        selected_rating: EloRating,
        human_color: chess.Color,
        ai_is_thinking: bool,
    ) -> int:
        top = 24
        header_lines = [
            ("Xadrez Simples", self.title_font),
            (f"Rating IA: {selected_rating.label}", self.body_font),
            (f"Humano: {'Brancas' if human_color == chess.WHITE else 'Pretas'}", self.body_font),
            (f"IA: {'Pensando...' if ai_is_thinking else 'Aguardando'}", self.body_font),
        ]
        for line, font in header_lines:
            text_surface = self._render_text(font, line)
            self.screen.blit(text_surface, (left, top))
            top += 46
        return top

    def _draw_panel_messages(self, session: GameSession, left: int, top: int) -> int:
        top = self._draw_wrapped_text(
            text=session.status_message(),
            font=self.body_font,
            color=self.palette.text,
            left=left,
            top=top,
            max_width=self.display_settings.side_panel_width - 44,
            line_height=28,
        ) + 10
        if session.move_error_message:
            top = self._draw_wrapped_text(
                text=session.move_error_message,
                font=self.small_font,
                color=self.palette.danger,
                left=left,
                top=top,
                max_width=self.display_settings.side_panel_width - 44,
                line_height=23,
            ) + 10
        return top

    def _draw_move_history(self, session: GameSession, left: int, top: int) -> None:
        title = self._render_text(self.body_font, "Histórico")
        self.screen.blit(title, (left, top))
        move_stack = self._format_move_history(session)

        for index in range(0, len(move_stack), 2):
            move_number = (len(session.board.move_stack[: index + 1]) + 1) // 2
            white_move = move_stack[index]
            black_move = move_stack[index + 1] if index + 1 < len(move_stack) else ""
            row_surface = self._render_text(
                self.small_font,
                f"{move_number}. {white_move} {black_move}".strip(),
            )
            self.screen.blit(row_surface, (left, top + 34 + (index // 2) * 24))

    def _draw_promotion_overlay(self, turn_color: chess.Color) -> None:
        shadow = pygame.Surface(
            (self.display_settings.window_width, self.display_settings.window_height),
            pygame.SRCALPHA,
        )
        shadow.fill((0, 0, 0, 120))
        self.screen.blit(shadow, (0, 0))

        overlay_rect = self._promotion_overlay_rect()
        pygame.draw.rect(self.screen, self.palette.panel, overlay_rect, border_radius=14)
        pygame.draw.rect(self.screen, self.palette.text, overlay_rect, width=2, border_radius=14)

        title = self._render_text(self.body_font, "Escolha a promoção")
        self.screen.blit(title, title.get_rect(center=(overlay_rect.centerx, overlay_rect.top + 28)))

        option_width = overlay_rect.width // len(PROMOTION_PIECES)
        for index, piece_type in enumerate(PROMOTION_PIECES):
            option_rect = pygame.Rect(
                overlay_rect.left + (index * option_width),
                overlay_rect.top + 56,
                option_width,
                overlay_rect.height - 72,
            )
            pygame.draw.rect(
                self.screen,
                self.palette.background,
                option_rect.inflate(-8, -8),
                border_radius=10,
            )
            piece = chess.Piece(piece_type, turn_color)
            sprite = self.piece_factory.get_sprite(piece)
            sprite_rect = sprite.get_rect(center=option_rect.center)
            self.screen.blit(sprite, sprite_rect)

    def _promotion_overlay_rect(self) -> pygame.Rect:
        width = 420
        height = 180
        left = (self.display_settings.window_width - width) // 2
        top = (self.display_settings.window_height - height) // 2
        return pygame.Rect(left, top, width, height)

    def _draw_menu_background(self) -> None:
        self.screen.fill(self.palette.background)
        header_rect = pygame.Rect(72, 52, self.display_settings.window_width - 144, 116)
        pygame.draw.rect(self.screen, self.palette.panel, header_rect, border_radius=18)
        pygame.draw.rect(self.screen, self.palette.light_square, header_rect, width=3, border_radius=18)

        tile_size = 42
        for file_index in range(12):
            color = self.palette.light_square if file_index % 2 == 0 else self.palette.dark_square
            rect = pygame.Rect(198 + file_index * tile_size, 584, tile_size, tile_size)
            pygame.draw.rect(self.screen, color, rect, border_radius=4)

    def _draw_color_button(self, button: ColorButton, selected_color: chess.Color) -> None:
        is_selected = button.color == selected_color
        fill_color = self.palette.accent if is_selected else self.palette.panel
        pygame.draw.rect(self.screen, fill_color, button.rect, border_radius=12)
        pygame.draw.rect(self.screen, self.palette.light_square, button.rect, width=2, border_radius=12)
        label = "Brancas" if button.color == chess.WHITE else "Pretas"
        label_surface = self._render_text(self.small_font, label)
        label_rect = pygame.Rect(button.rect.left + 40, button.rect.top, button.rect.width - 52, button.rect.height)
        if is_selected:
            self._draw_selected_color_icon(button)
        self.screen.blit(label_surface, label_surface.get_rect(center=label_rect.center))

    def _draw_selected_color_icon(self, button: ColorButton) -> None:
        marker_piece = chess.Piece(chess.PAWN, button.color)
        marker_surface = pygame.transform.smoothscale(
            self.piece_factory.get_sprite(marker_piece),
            (28, 28),
        )
        marker_rect = marker_surface.get_rect(midleft=(button.rect.left + 16, button.rect.centery))
        self.screen.blit(marker_surface, marker_rect)

    def _draw_rating_slider(self, selected_rating: EloRating) -> None:
        slider = self.rating_slider()
        slider_text_color = (255, 255, 255)
        label_surface = self._render_text(
            self.body_font,
            f"Elo selecionado: {selected_rating.label}",
            slider_text_color,
        )
        self.screen.blit(label_surface, label_surface.get_rect(center=(450, slider.rect.top - 28)))

        pygame.draw.line(
            self.screen,
            self.palette.light_square,
            slider.rect.midleft,
            slider.rect.midright,
            width=6,
        )

        for rating in ELO_RATINGS:
            x_position = self._slider_x_for_rating(rating)
            pygame.draw.circle(
                self.screen,
                self.palette.light_square,
                (x_position, slider.rect.centery),
                5,
            )
            tick_label = self._render_text(self.small_font, rating.label, slider_text_color)
            self.screen.blit(
                tick_label,
                tick_label.get_rect(center=(x_position, slider.rect.bottom + 18)),
            )

        knob_center = (self._slider_x_for_rating(selected_rating), slider.rect.centery)
        pygame.draw.circle(self.screen, self.palette.accent, knob_center, slider.knob_radius)
        pygame.draw.circle(self.screen, self.palette.text, knob_center, slider.knob_radius, width=2)

    def _draw_action_button(self, button: ActionButton, fill_color: tuple[int, int, int]) -> None:
        pygame.draw.rect(self.screen, fill_color, button.rect, border_radius=12)
        pygame.draw.rect(self.screen, self.palette.light_square, button.rect, width=2, border_radius=12)
        label_surface = self._render_text(self.small_font, button.label)
        self.screen.blit(label_surface, label_surface.get_rect(center=button.rect.center))

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
        return self.text_renderer.wrap(
            surface=self.screen,
            font=font,
            text=text,
            color=color,
            left=left,
            top=top,
            max_width=max_width,
            line_height=line_height,
        )

    def _format_move_history(self, session: GameSession) -> list[str]:
        return format_move_history(session)

    def _slider_x_for_rating(self, rating: EloRating) -> int:
        slider = self.rating_slider()
        index = ELO_RATINGS.index(rating)
        if len(ELO_RATINGS) == 1:
            return slider.rect.left
        step_width = slider.rect.width / (len(ELO_RATINGS) - 1)
        return round(slider.rect.left + index * step_width)

    def _render_text(
        self,
        font: UiFont,
        text: str,
        color: tuple[int, int, int] | None = None,
    ) -> pygame.Surface:
        return self.text_renderer.render(font, text, color)

    def _square_from_display(self, display_file: int, display_rank: int, human_color: chess.Color) -> chess.Square:
        if human_color == chess.WHITE:
            return chess.square(display_file, 7 - display_rank)
        return chess.square(7 - display_file, display_rank)

    def _display_from_square(self, square: chess.Square, human_color: chess.Color) -> tuple[int, int]:
        file_index = chess.square_file(square)
        rank_index = chess.square_rank(square)
        if human_color == chess.WHITE:
            return file_index, 7 - rank_index
        return 7 - file_index, rank_index
