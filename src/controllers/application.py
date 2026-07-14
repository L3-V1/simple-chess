from __future__ import annotations

import sys
from pathlib import Path

import chess
import pygame

from src.controllers.menu_state import MenuSelection
from src.core import EloRating
from src.models import GameSession
from src.services import ComputerPlayer, SoundEffect, SoundManager
from src.views import ChessRenderer

SOUNDS_DIRECTORY = Path(__file__).resolve().parent.parent.parent / "assets" / "sounds"


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
        self.sound_manager = self._build_sound_manager()
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
        selection = MenuSelection(
            rating=self.selected_rating,
            color=self.human_color,
        )
        while True:
            if self._process_menu_events(selection):
                return selection.rating, selection.color
            self.renderer.draw_menu(selection.rating, selection.color)

    def _process_menu_events(self, selection: MenuSelection) -> bool:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self._shutdown()
            if event.type == pygame.MOUSEMOTION and event.buttons[0]:
                self._update_menu_rating(selection, event.pos)
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if self._handle_menu_click(selection, event.pos):
                    return True
        return False

    def _handle_menu_click(self, selection: MenuSelection, position: tuple[int, int]) -> bool:
        color = self._color_from_position(position)
        if color is not None:
            self._update_menu_color(selection, color)
            return False

        rating = self.renderer.rating_from_slider_position(position)
        if rating is not None:
            selection.select_rating(rating)
            return False

        return self.renderer.menu_start_button().rect.collidepoint(position)

    def _update_menu_rating(self, selection: MenuSelection, position: tuple[int, int]) -> None:
        rating = self.renderer.rating_from_slider_position(position)
        if rating is not None:
            selection.select_rating(rating)

    def _update_menu_color(self, selection: MenuSelection, color: chess.Color) -> None:
        if selection.select_color(color):
            self.sound_manager.play(SoundEffect.MENU_SELECT)

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
                self._play_last_move_sound()
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
            self._play_last_move_sound()

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
            self._play_last_move_sound()
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

    def _play_last_move_sound(self) -> None:
        if self.session.last_move_was_castling:
            self.sound_manager.play(SoundEffect.CASTLING)
            return
        if self.session.last_move_was_capture:
            self.sound_manager.play(SoundEffect.CAPTURE)
            return
        self.sound_manager.play(SoundEffect.MOVE)

    def _build_sound_manager(self) -> SoundManager:
        return SoundManager(
            sound_paths={
                SoundEffect.MOVE: SOUNDS_DIRECTORY / "chess_move_wood.wav",
                SoundEffect.CAPTURE: SOUNDS_DIRECTORY / "chess_capture.wav",
                SoundEffect.CASTLING: SOUNDS_DIRECTORY / "chess_castling.wav",
                SoundEffect.MENU_SELECT: SOUNDS_DIRECTORY / "chess_menu_select.wav",
            }
        )

    def _shutdown(self) -> None:
        pygame.quit()
        sys.exit(0)
