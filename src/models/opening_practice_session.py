from __future__ import annotations

from dataclasses import dataclass, field

import chess

from .game_session import GameSession
from .opening_line import OpeningLine


@dataclass
class OpeningPracticeSession:
    """Guide the player through a stored opening line move by move."""

    opening: OpeningLine
    session: GameSession = field(default_factory=GameSession)
    current_move_index: int = 0

    def start(self) -> None:
        """Initialize practice and advance opponent moves when needed."""
        self.session.reset()
        self.current_move_index = 0
        self.session.move_error_message = ""
        self._play_opponent_responses()

    @property
    def player_color(self) -> chess.Color:
        """Expose the practicing side color."""
        return self.opening.player_color

    def is_completed(self) -> bool:
        """Return whether the full opening line has been completed."""
        return self.current_move_index >= len(self.opening.moves_uci)

    def instruction_message(self) -> str:
        """Build the status text shown during practice."""
        if self.is_completed():
            return f"Abertura concluída: {self.opening.name}."
        side_to_move = "Brancas" if self.session.board.turn == chess.WHITE else "Pretas"
        return f"Treino: {self.opening.name}. Vez das {side_to_move.lower()}."

    def handle_player_click(self, square: chess.Square) -> bool:
        """Handle a click and advance only when the expected move is played."""
        if self.is_completed():
            self.session.move_error_message = "Essa sequência já foi concluída."
            return False
        if self.session.pending_promotion is not None:
            self.session.move_error_message = "Escolha a peça da promoção para continuar."
            return False

        expected_move = self._expected_player_move()
        if expected_move is None:
            self.session.move_error_message = "A linha atual aguarda a resposta do adversário."
            return False

        if self.session.selected_square is None:
            self.session.select_square(square)
            return False
        if square == self.session.selected_square:
            self.session.clear_selection()
            return False

        piece = self.session.board.piece_at(square)
        if piece is not None and piece.color == self.session.board.turn:
            self.session.select_square(square)
            return False

        return self._attempt_expected_move(square, expected_move)

    def choose_promotion(self, promotion_piece: chess.PieceType) -> bool:
        """Resolve promotion only when it matches the stored opening move."""
        expected_move = self._expected_player_move()
        if expected_move is None or self.session.pending_promotion is None:
            return False
        if expected_move.promotion != promotion_piece:
            self.session.move_error_message = "Essa promoção não corresponde à abertura treinada."
            return False
        self.session.apply_move(expected_move)
        self.current_move_index += 1
        self._play_opponent_responses()
        return True

    def _attempt_expected_move(self, target_square: chess.Square, expected_move: chess.Move) -> bool:
        selected_square = self.session.selected_square
        if selected_square is None:
            return False

        candidate_moves = [
            move
            for move in self.session.board.legal_moves
            if move.from_square == selected_square and move.to_square == target_square
        ]
        if not candidate_moves:
            self.session.move_error_message = "Movimento ilegal para a peça selecionada."
            return False
        if expected_move not in candidate_moves:
            self.session.move_error_message = "Lance incorreto para a abertura treinada. Tente novamente."
            return False
        if len(candidate_moves) > 1:
            self.session.pending_promotion = (selected_square, target_square)
            self.session.move_error_message = "Escolha a peça da promoção correta."
            return False

        self.session.apply_move(expected_move)
        self.current_move_index += 1
        self._play_opponent_responses()
        return True

    def _expected_player_move(self) -> chess.Move | None:
        if self.is_completed():
            return None
        move = chess.Move.from_uci(self.opening.moves_uci[self.current_move_index])
        if self.session.board.turn != self.player_color:
            return None
        return move

    def _play_opponent_responses(self) -> None:
        while not self.is_completed() and self.session.board.turn != self.player_color:
            move = chess.Move.from_uci(self.opening.moves_uci[self.current_move_index])
            self.session.apply_move(move)
            self.current_move_index += 1
