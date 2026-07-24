from __future__ import annotations

from dataclasses import dataclass, field
from typing import Iterable

import chess


PROMOTION_PIECES = (
    chess.QUEEN,
    chess.ROOK,
    chess.BISHOP,
    chess.KNIGHT,
)


@dataclass
class GameSession:
    board: chess.Board = field(default_factory=chess.Board)
    selected_square: chess.Square | None = None
    legal_targets: list[chess.Square] = field(default_factory=list)
    pending_promotion: tuple[chess.Square, chess.Square] | None = None
    last_move: chess.Move | None = None
    last_move_was_capture: bool = False
    last_move_was_castling: bool = False
    move_error_message: str = ""
    resigned_color: chess.Color | None = None

    def has_moves(self) -> bool:
        """Return whether the current game already contains played moves."""
        return bool(self.board.move_stack)

    def reset(self) -> None:
        """Reset the match state to a new game."""
        self.board.reset()
        self.clear_selection()
        self.last_move = None
        self.last_move_was_capture = False
        self.last_move_was_castling = False
        self.move_error_message = ""
        self.resigned_color = None

    def clear_selection(self) -> None:
        """Clear current selection and promotion state."""
        self.selected_square = None
        self.legal_targets.clear()
        self.pending_promotion = None

    def select_square(self, square: chess.Square) -> None:
        """Select a player piece and cache all reachable target squares."""
        if self.resigned_color is not None:
            self.move_error_message = "A partida já foi encerrada."
            self.clear_selection()
            return

        piece = self.board.piece_at(square)
        if piece is None or piece.color != self.board.turn:
            self.move_error_message = "Selecione uma de suas próprias peças."
            self.clear_selection()
            return

        legal_moves = [move for move in self.board.legal_moves if move.from_square == square]
        if not legal_moves:
            self.move_error_message = "Essa peça não possui movimentos legais."
            self.clear_selection()
            return

        self.selected_square = square
        self.legal_targets = [move.to_square for move in legal_moves]
        self.move_error_message = ""

    def handle_player_click(self, square: chess.Square) -> bool:
        """Handle a click on the board and apply a legal move when possible."""
        if self.pending_promotion is not None:
            self.move_error_message = "Escolha a peça da promoção para continuar."
            return False

        if self.selected_square is None:
            self.select_square(square)
            return False

        if square == self.selected_square:
            self.clear_selection()
            return False

        piece = self.board.piece_at(square)
        if piece is not None and piece.color == self.board.turn:
            self.select_square(square)
            return False

        return self._attempt_selected_move(square)

    def choose_promotion(self, promotion_piece: chess.PieceType) -> bool:
        """Resolve a pending promotion choice."""
        if self.pending_promotion is None:
            return False
        if promotion_piece not in PROMOTION_PIECES:
            self.move_error_message = "Peça de promoção inválida."
            return False

        from_square, to_square = self.pending_promotion
        move = chess.Move(from_square, to_square, promotion=promotion_piece)
        if move not in self.board.legal_moves:
            self.move_error_message = "A promoção selecionada não é legal."
            return False

        self.apply_move(move)
        return True

    def apply_move(self, move: chess.Move) -> None:
        """Push a legal move to the board and update UI-facing session state."""
        if move not in self.board.legal_moves:
            raise ValueError(f"Attempted to apply illegal move: {move.uci()}")
        self.last_move_was_capture = self.board.is_capture(move)
        self.last_move_was_castling = self.board.is_castling(move)
        self.board.push(move)
        self.last_move = move
        self.move_error_message = ""
        self.selected_square = None
        self.legal_targets.clear()
        self.pending_promotion = None

    def is_human_turn(self, human_color: chess.Color) -> bool:
        """Return whether it is the human player's turn."""
        return self.board.turn == human_color and not self.is_finished()

    def resign(self, color: chess.Color) -> None:
        """Mark the game as finished by resignation."""
        self.resigned_color = color
        self.move_error_message = ""
        self.clear_selection()

    def is_finished(self) -> bool:
        """Return whether the game has ended by rules or resignation."""
        return self.resigned_color is not None or self.board.is_game_over(claim_draw=True)

    def export_san_moves(self) -> str:
        """Return the played move sequence formatted in SAN notation."""
        replay_board = chess.Board()
        san_moves: list[str] = []

        for move in self.board.move_stack:
            san_moves.append(replay_board.san(move))
            replay_board.push(move)

        return " ".join(san_moves)

    def status_message(self) -> str:
        """Build the main status message shown in the side panel."""
        if self.resigned_color is not None:
            winner = "Pretas" if self.resigned_color == chess.WHITE else "Brancas"
            return f"Partida encerrada por desistência. {winner} vencem."
        if self.board.is_checkmate():
            winner = "Pretas" if self.board.turn == chess.WHITE else "Brancas"
            return f"Xeque-mate. {winner} vencem."
        if self.board.is_stalemate():
            return "Empate por afogamento."
        if self.board.is_insufficient_material():
            return "Empate por material insuficiente."
        if self.board.can_claim_threefold_repetition():
            return "Empate pode ser reclamado por repetição."
        if self.board.can_claim_fifty_moves():
            return "Empate pode ser reclamado pela regra dos 50 lances."
        if self.pending_promotion is not None:
            return "Escolha a peça da promoção."
        if self.board.is_check():
            side_to_move = "Brancas" if self.board.turn == chess.WHITE else "Pretas"
            return f"{side_to_move} estão em xeque."
        return "Vez das brancas." if self.board.turn == chess.WHITE else "Vez das pretas."

    def _attempt_selected_move(self, target_square: chess.Square) -> bool:
        if self.selected_square is None:
            return False

        candidate_moves = list(self._matching_moves(self.selected_square, target_square))
        if not candidate_moves:
            self.move_error_message = "Movimento ilegal para a peça selecionada."
            return False

        if len(candidate_moves) > 1:
            self.pending_promotion = (self.selected_square, target_square)
            self.move_error_message = "Promoção obrigatória."
            return False

        self.apply_move(candidate_moves[0])
        return True

    def _matching_moves(
        self,
        from_square: chess.Square,
        to_square: chess.Square,
    ) -> Iterable[chess.Move]:
        return (
            move
            for move in self.board.legal_moves
            if move.from_square == from_square and move.to_square == to_square
        )
