from __future__ import annotations

import sys
from pathlib import Path

import chess
import pygame

from src.controllers.menu_state import MenuSelection
from src.controllers.screen_state import AppScreen
from src.core import EloRating
from src.models import GameRuntime, TrainingMoveFeedback, TrainingRuntime
from src.services import OpeningCatalog, SoundEffect, SoundManager
from src.views import ChessRenderer

SOUNDS_DIRECTORY = Path(__file__).resolve().parent.parent.parent / "assets" / "sounds"
OPENINGS_STORAGE_PATH = Path(__file__).resolve().parent.parent.parent / "data" / "openings.json"


class ChessApplication:
    def __init__(self) -> None:
        pygame.init()
        pygame.font.init()
        self.renderer = ChessRenderer()
        self.runtime = GameRuntime()
        self.training_runtime = TrainingRuntime()
        self.current_screen = AppScreen.MENU
        self.sound_manager = self._build_sound_manager()
        self.opening_catalog = OpeningCatalog(OPENINGS_STORAGE_PATH)
        self.sound_manager.initialize()
        self._refresh_openings()

    def run(self) -> None:
        """Run the top-level application loop."""
        try:
            while True:
                self._process_current_screen()
                self._draw_current_screen()
        except pygame.error as error:
            raise RuntimeError("Pygame failed to initialize the chess application.") from error
        finally:
            pygame.quit()

    def _process_current_screen(self) -> None:
        if self.current_screen == AppScreen.MENU:
            self._process_menu_screen()
            return
        if self.current_screen == AppScreen.GAME:
            self._process_game_screen()
            return
        self._process_training_screen()

    def _draw_current_screen(self) -> None:
        if self.current_screen == AppScreen.MENU:
            self.renderer.draw_menu(self.runtime.selected_rating, self.runtime.human_color)
            return
        if self.current_screen == AppScreen.GAME:
            self.renderer.draw(
                session=self.runtime.session,
                selected_rating=self.runtime.selected_rating,
                human_color=self.runtime.human_color,
                ai_is_thinking=self.runtime.ai_is_thinking,
            )
            return
        self.renderer.draw_training(self.training_runtime)

    def _process_menu_screen(self) -> None:
        selection = MenuSelection(
            rating=self.runtime.selected_rating,
            color=self.runtime.human_color,
        )
        menu_action = self._process_menu_events(selection)
        self.runtime.apply_menu_selection(selection.rating, selection.color)
        if menu_action == "start_game":
            self.runtime.reset_match()
            self.current_screen = AppScreen.GAME
        if menu_action == "open_training":
            self.training_runtime.end_practice()
            self.current_screen = AppScreen.TRAINING

    def _process_menu_events(self, selection: MenuSelection) -> str | None:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self._shutdown()
            if event.type == pygame.MOUSEMOTION and event.buttons[0]:
                self._update_menu_rating(selection, event.pos)
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                action = self._handle_menu_click(selection, event.pos)
                if action is not None:
                    return action
        return None

    def _handle_menu_click(self, selection: MenuSelection, position: tuple[int, int]) -> str | None:
        color = self._color_from_position(position)
        if color is not None:
            self._update_menu_color(selection, color)
            return None

        rating = self.renderer.rating_from_slider_position(position)
        if rating is not None:
            selection.select_rating(rating)
            return None
        if self.renderer.menu_start_button().rect.collidepoint(position):
            return "start_game"
        if self.renderer.menu_training_button().rect.collidepoint(position):
            return "open_training"
        return None

    def _update_menu_rating(self, selection: MenuSelection, position: tuple[int, int]) -> None:
        rating = self.renderer.rating_from_slider_position(position)
        if rating is not None:
            selection.select_rating(rating)

    def _update_menu_color(self, selection: MenuSelection, color: chess.Color) -> None:
        if selection.select_color(color):
            self.sound_manager.play(SoundEffect.MENU_SELECT)

    def _process_game_screen(self) -> None:
        self._handle_game_events()
        if self._should_computer_play():
            self._perform_computer_move()

    def _handle_game_events(self) -> None:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self._shutdown()
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                self._handle_left_click(event.pos)

    def _handle_left_click(self, position: tuple[int, int]) -> None:
        action_button = self.renderer.primary_action_button(self.runtime.session)
        if action_button.rect.collidepoint(position):
            self._handle_primary_action()
            return
        if not self.runtime.session.is_human_turn(self.runtime.human_color):
            return
        if self.runtime.session.pending_promotion is not None:
            self._handle_promotion_click(position)
            return

        square = self.renderer.pixel_to_square(position, self.runtime.human_color)
        if square is None:
            return

        try:
            if self.runtime.session.handle_player_click(square):
                self._play_last_move_sound()
        except ValueError as error:
            self.runtime.session.move_error_message = str(error)

    def _handle_primary_action(self) -> None:
        if self.runtime.session.is_finished():
            self.current_screen = AppScreen.MENU
            return
        self.runtime.session.resign(self.runtime.human_color)

    def _handle_promotion_click(self, position: tuple[int, int]) -> None:
        promotion_piece = self.renderer.promotion_button_at(position)
        if promotion_piece is not None and self.runtime.session.choose_promotion(promotion_piece):
            self._play_last_move_sound()

    def _should_computer_play(self) -> bool:
        return (
            not self.runtime.ai_is_thinking
            and not self.runtime.session.is_finished()
            and self.runtime.session.board.turn != self.runtime.human_color
        )

    def _perform_computer_move(self) -> None:
        self.runtime.begin_ai_turn()
        self.renderer.draw(
            session=self.runtime.session,
            selected_rating=self.runtime.selected_rating,
            human_color=self.runtime.human_color,
            ai_is_thinking=True,
        )
        try:
            move = self.runtime.computer_player.choose_move(self.runtime.session.board.copy(stack=True))
            self.runtime.session.apply_move(move)
            self._play_last_move_sound()
        except ValueError as error:
            self.runtime.session.move_error_message = str(error)
        finally:
            self.runtime.finish_ai_turn()

    def _process_training_screen(self) -> None:
        if self.training_runtime.practice_session is None:
            self._handle_training_library_events()
            return
        self._handle_training_practice_events()

    def _handle_training_library_events(self) -> None:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self._shutdown()
            if event.type == pygame.TEXTINPUT:
                self._append_training_input(event.text)
            if event.type == pygame.KEYDOWN:
                self._handle_training_keydown(event)
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                self._handle_training_library_click(event.pos)

    def _append_training_input(self, text: str) -> None:
        if self.training_runtime.active_input == "name":
            self.training_runtime.opening_name_input += text
            return
        if self.training_runtime.active_input == "moves":
            self.training_runtime.opening_moves_input += text

    def _handle_training_keydown(self, event: pygame.event.Event) -> None:
        if event.key == pygame.K_ESCAPE:
            self._return_to_menu()
            return
        if event.key == pygame.K_BACKSPACE:
            self._remove_training_input_character()
            return
        if event.key == pygame.K_RETURN:
            self._save_training_opening()

    def _remove_training_input_character(self) -> None:
        if self.training_runtime.active_input == "name":
            self.training_runtime.opening_name_input = self.training_runtime.opening_name_input[:-1]
            return
        if self.training_runtime.active_input == "moves":
            self.training_runtime.opening_moves_input = self.training_runtime.opening_moves_input[:-1]

    def _handle_training_library_click(self, position: tuple[int, int]) -> None:
        if self.renderer.training_library_back_button().rect.collidepoint(position):
            self._return_to_menu()
            return
        if self.renderer.training_save_opening_button().rect.collidepoint(position):
            self._save_training_opening()
            return
        if self.renderer.training_delete_button().rect.collidepoint(position):
            self._delete_selected_opening()
            return
        if self.renderer.training_start_button().rect.collidepoint(position):
            self._start_selected_opening_practice()
            return
        if self.renderer.training_name_input().rect.collidepoint(position):
            self.training_runtime.active_input = "name"
            return
        if self.renderer.training_moves_input().rect.collidepoint(position):
            self.training_runtime.active_input = "moves"
            return

        color = self._training_color_from_position(position)
        if color is not None:
            self.training_runtime.opening_color = color
            self.sound_manager.play(SoundEffect.MENU_SELECT)
            return

        for opening, rect in self.renderer.training_opening_rows(self.training_runtime):
            if rect.collidepoint(position):
                if self.training_runtime.select_opening(opening.name):
                    self.sound_manager.play(SoundEffect.MENU_SELECT)
                return

        self.training_runtime.active_input = None

    def _save_training_opening(self) -> None:
        try:
            opening = self.opening_catalog.add_opening(
                name=self.training_runtime.opening_name_input,
                player_color=self.training_runtime.opening_color,
                moves_text=self.training_runtime.opening_moves_input,
            )
        except ValueError as error:
            self.training_runtime.feedback_message = str(error)
            return

        self._refresh_openings()
        self.training_runtime.select_opening(opening.name)
        self.training_runtime.feedback_message = "Abertura salva com sucesso."
        self.training_runtime.clear_form()

    def _start_selected_opening_practice(self) -> None:
        opening = self.training_runtime.selected_opening()
        if opening is None:
            self.training_runtime.feedback_message = "Selecione uma abertura para praticar."
            return
        self.training_runtime.begin_practice(opening)

    def _delete_selected_opening(self) -> None:
        opening = self.training_runtime.selected_opening()
        if opening is None:
            self.training_runtime.feedback_message = "Selecione uma abertura para excluir."
            return
        try:
            self.opening_catalog.delete_opening(opening.name)
        except ValueError as error:
            self.training_runtime.feedback_message = str(error)
            return
        self._refresh_openings()
        self.training_runtime.feedback_message = "Abertura excluída com sucesso."

    def _handle_training_practice_events(self) -> None:
        practice = self.training_runtime.practice_session
        if practice is None:
            return
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self._shutdown()
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                self.training_runtime.end_practice()
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if self.renderer.training_practice_back_button().rect.collidepoint(event.pos):
                    self._return_to_menu()
                    return
                if self.renderer.training_finish_button().rect.collidepoint(event.pos):
                    self.training_runtime.end_practice()
                    return
                if practice.session.pending_promotion is not None:
                    self._handle_training_promotion_click(event.pos)
                    continue
                square = self.renderer.training_pixel_to_square(event.pos, practice.player_color)
                if square is None:
                    continue
                moved = practice.handle_player_click(square)
                self._play_training_attempt_sound(moved)

    def _handle_training_promotion_click(self, position: tuple[int, int]) -> None:
        practice = self.training_runtime.practice_session
        if practice is None:
            return
        promotion_piece = self.renderer.training_promotion_button_at(position)
        if promotion_piece is None:
            return
        moved = practice.choose_promotion(promotion_piece)
        self._play_training_attempt_sound(moved)

    def _training_color_from_position(self, position: tuple[int, int]) -> chess.Color | None:
        for button in self.renderer.training_color_buttons():
            if button.rect.collidepoint(position):
                return button.color
        return None

    def _play_last_move_sound(self) -> None:
        if self.runtime.session.last_move_was_castling:
            self.sound_manager.play(SoundEffect.CASTLING)
            return
        if self.runtime.session.last_move_was_capture:
            self.sound_manager.play(SoundEffect.CAPTURE)
            return
        self.sound_manager.play(SoundEffect.MOVE)

    def _play_training_move_sound(self) -> None:
        practice = self.training_runtime.practice_session
        if practice is None:
            return
        if practice.session.last_move_was_castling:
            self.sound_manager.play(SoundEffect.CASTLING)
            return
        if practice.session.last_move_was_capture:
            self.sound_manager.play(SoundEffect.CAPTURE)
            return
        self.sound_manager.play(SoundEffect.MOVE)

    def _play_training_attempt_sound(self, moved: bool) -> None:
        practice = self.training_runtime.practice_session
        if practice is None:
            return
        if practice.last_feedback == TrainingMoveFeedback.INCORRECT:
            self.sound_manager.play(SoundEffect.TRAINING_INCORRECT)
            return
        if moved and practice.last_feedback == TrainingMoveFeedback.CORRECT:
            self.sound_manager.play(SoundEffect.TRAINING_CORRECT)
            self._play_training_move_sound()

    def _refresh_openings(self) -> None:
        openings = self.opening_catalog.load_openings()
        self.training_runtime.set_openings(openings)

    def _return_to_menu(self) -> None:
        self.training_runtime.end_practice()
        self.training_runtime.active_input = None
        self.current_screen = AppScreen.MENU

    def _color_from_position(self, position: tuple[int, int]) -> chess.Color | None:
        for button in self.renderer.color_buttons():
            if button.rect.collidepoint(position):
                return button.color
        return None

    def _build_sound_manager(self) -> SoundManager:
        return SoundManager(
            sound_paths={
                SoundEffect.MOVE: SOUNDS_DIRECTORY / "chess_move_wood.wav",
                SoundEffect.CAPTURE: SOUNDS_DIRECTORY / "chess_capture.wav",
                SoundEffect.CASTLING: SOUNDS_DIRECTORY / "chess_castling.wav",
                SoundEffect.MENU_SELECT: SOUNDS_DIRECTORY / "chess_menu_select.wav",
                SoundEffect.TRAINING_CORRECT: SOUNDS_DIRECTORY / "training_correct.wav",
                SoundEffect.TRAINING_INCORRECT: SOUNDS_DIRECTORY / "training_incorrect.wav",
            }
        )

    def _shutdown(self) -> None:
        pygame.quit()
        sys.exit(0)
