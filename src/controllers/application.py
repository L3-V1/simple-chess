from __future__ import annotations

import sys
from pathlib import Path

import chess
import pygame

from src.core import EloRating
from src.models import GameSession
from src.services import ComputerPlayer, SoundManager
from src.views import ChessRenderer


class ChessApplication:
    def __init__(self) -> None:
        pygame.init()
        pygame.font.init()
        self.renderer = ChessRenderer()
        self.session = GameSession()
        self.selected_rating = EloRating.ELO_1500
        self.human_color = chess.WHITE
        self.computer_player = ComputerPlayer(self.selected_rating)
        self.ai_is_thinking = False
        self.sound_manager = SoundManager(
            move_sound_path=Path(__file__).resolve().parent.parent.parent / "assets" / "sounds" / "chess_move_wood.wav"
        )
        self.sound_manager.initialize()

    def run(self) -> None:
        """Run the menu flow followed by the main pygame loop."""
        try:
            self.selected_rating, self.human_color = self._run_menu()
            self._start_new_game()
            self._run_game_loop()
        except pygame.error as error:
            raise RuntimeError("Pygame failed to initialize the chess application.") from error
        finally:
            pygame.quit()

    def _run_menu(self) -> tuple[EloRating, chess.Color]:
        selected_rating = self.selected_rating
        selected_color = self.human_color
        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self._shutdown()
                if event.type == pygame.MOUSEMOTION and event.buttons[0]:
                    rating = self.renderer.rating_from_slider_position(event.pos)
                    if rating is not None:
                        selected_rating = rating
                if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    color = self._color_from_position(event.pos)
                    if color is not None:
                        selected_color = color
                        continue
                    rating = self.renderer.rating_from_slider_position(event.pos)
                    if rating is not None:
                        selected_rating = rating
                        continue
                    if self.renderer.menu_start_button().rect.collidepoint(event.pos):
                        return selected_rating, selected_color
            self.renderer.draw_menu(selected_rating, selected_color)

    def _run_game_loop(self) -> None:
        while True:
            self._handle_events()
            if self._should_computer_play():
                self._perform_computer_move()
            self.renderer.draw(
                session=self.session,
                selected_rating=self.selected_rating,
                human_color=self.human_color,
                ai_is_thinking=self.ai_is_thinking,
            )

    def _handle_events(self) -> None:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self._shutdown()
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                self._handle_left_click(event.pos)

    def _handle_left_click(self, position: tuple[int, int]) -> None:
        action_button = self.renderer.primary_action_button(self.session)
        if action_button.rect.collidepoint(position):
            self._handle_primary_action()
            return

        if not self.session.is_human_turn(self.human_color):
            return
        if self.session.pending_promotion is not None:
            self._handle_promotion_click(position)
            return

        square = self.renderer.pixel_to_square(position, self.human_color)
        if square is None:
            return

        try:
            if self.session.handle_player_click(square):
                self.sound_manager.play_move()
        except ValueError as error:
            self.session.move_error_message = str(error)

    def _handle_primary_action(self) -> None:
        if self.session.is_finished():
            self.selected_rating, self.human_color = self._run_menu()
            self._start_new_game()
            return
        self.session.resign(self.human_color)

    def _handle_promotion_click(self, position: tuple[int, int]) -> None:
        promotion_piece = self.renderer.promotion_button_at(position)
        if promotion_piece is not None and self.session.choose_promotion(promotion_piece):
            self.sound_manager.play_move()

    def _should_computer_play(self) -> bool:
        return (
            not self.ai_is_thinking
            and not self.session.is_finished()
            and self.session.board.turn != self.human_color
        )

    def _perform_computer_move(self) -> None:
        self.ai_is_thinking = True
        self.renderer.draw(
            session=self.session,
            selected_rating=self.selected_rating,
            human_color=self.human_color,
            ai_is_thinking=True,
        )
        try:
            move = self.computer_player.choose_move(self.session.board.copy(stack=True))
            self.session.apply_move(move)
            self.sound_manager.play_move()
        except ValueError as error:
            self.session.move_error_message = str(error)
        finally:
            self.ai_is_thinking = False

    def _start_new_game(self) -> None:
        self.session.reset()
        self.computer_player = ComputerPlayer(self.selected_rating)
        self.ai_is_thinking = False

    def _color_from_position(self, position: tuple[int, int]) -> chess.Color | None:
        for button in self.renderer.color_buttons():
            if button.rect.collidepoint(position):
                return button.color
        return None

    def _shutdown(self) -> None:
        pygame.quit()
        sys.exit(0)
