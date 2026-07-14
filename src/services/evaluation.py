from __future__ import annotations

from dataclasses import dataclass

import chess

from src.core import AiProfile
from src.services.evaluation_tables import (
    CENTER_SQUARES,
    EXTENDED_CENTER_SQUARES,
    MOBILITY_WEIGHTS,
    PIECE_SQUARE_TABLES,
    PIECE_VALUES,
)


@dataclass(frozen=True)
class BoardEvaluator:
    profile: AiProfile

    def evaluate(self, board: chess.Board, maximizing_color: chess.Color) -> int:
        """Return a score from the perspective of the maximizing player."""
        if board.is_checkmate():
            return -999_999 if board.turn == maximizing_color else 999_999
        if board.is_stalemate() or board.is_insufficient_material():
            return 0
        if board.can_claim_threefold_repetition() or board.can_claim_fifty_moves():
            return 0

        score = self._evaluate_material(board)
        score += self._evaluate_bishop_pair(board)
        score += self._evaluate_pawn_structure(board)
        score += self._evaluate_mobility(board)
        if self.profile.use_piece_square_tables:
            score += self._evaluate_piece_positions(board)
        if self.profile.use_center_control:
            score += self._evaluate_center_control(board)
            score += self._evaluate_king_safety(board)
        return score if maximizing_color == chess.WHITE else -score

    def _evaluate_material(self, board: chess.Board) -> int:
        material_score = 0
        for piece_type, piece_value in PIECE_VALUES.items():
            material_score += len(board.pieces(piece_type, chess.WHITE)) * piece_value
            material_score -= len(board.pieces(piece_type, chess.BLACK)) * piece_value
        return material_score

    def _evaluate_piece_positions(self, board: chess.Board) -> int:
        position_score = 0
        for square, piece in board.piece_map().items():
            table = PIECE_SQUARE_TABLES[piece.piece_type]
            lookup_square = square if piece.color == chess.WHITE else chess.square_mirror(square)
            adjustment = table[lookup_square]
            position_score += adjustment if piece.color == chess.WHITE else -adjustment
        return position_score

    def _evaluate_center_control(self, board: chess.Board) -> int:
        center_score = 0
        for square in CENTER_SQUARES:
            center_score += self._score_square_control(board, square, 18)
        for square in EXTENDED_CENTER_SQUARES:
            center_score += self._score_square_control(board, square, 6)
        return center_score

    def _score_square_control(self, board: chess.Board, square: chess.Square, weight: int) -> int:
        white_attackers = len(board.attackers(chess.WHITE, square))
        black_attackers = len(board.attackers(chess.BLACK, square))
        return (white_attackers - black_attackers) * weight

    def _evaluate_bishop_pair(self, board: chess.Board) -> int:
        score = 0
        if len(board.pieces(chess.BISHOP, chess.WHITE)) >= 2:
            score += 30
        if len(board.pieces(chess.BISHOP, chess.BLACK)) >= 2:
            score -= 30
        return score

    def _evaluate_pawn_structure(self, board: chess.Board) -> int:
        return self._score_pawns(board, chess.WHITE) - self._score_pawns(board, chess.BLACK)

    def _score_pawns(self, board: chess.Board, color: chess.Color) -> int:
        pawns = board.pieces(chess.PAWN, color)
        files = [0] * 8
        score = 0
        for square in pawns:
            files[chess.square_file(square)] += 1
            rank = chess.square_rank(square) if color == chess.WHITE else 7 - chess.square_rank(square)
            score += rank * 4
            if self._is_passed_pawn(board, square, color):
                score += 18 + rank * 10

        for count in files:
            if count > 1:
                score -= (count - 1) * 14
        return score

    def _is_passed_pawn(self, board: chess.Board, square: chess.Square, color: chess.Color) -> bool:
        enemy_color = not color
        file_index = chess.square_file(square)
        rank_index = chess.square_rank(square)
        files_to_check = range(max(0, file_index - 1), min(7, file_index + 1) + 1)
        ranks_to_check = range(rank_index + 1, 8) if color == chess.WHITE else range(rank_index - 1, -1, -1)

        for enemy_square in board.pieces(chess.PAWN, enemy_color):
            enemy_file = chess.square_file(enemy_square)
            enemy_rank = chess.square_rank(enemy_square)
            if enemy_file in files_to_check and enemy_rank in ranks_to_check:
                return False
        return True

    def _evaluate_mobility(self, board: chess.Board) -> int:
        white_score = self._mobility_for_color(board, chess.WHITE)
        black_score = self._mobility_for_color(board, chess.BLACK)
        return white_score - black_score

    def _mobility_for_color(self, board: chess.Board, color: chess.Color) -> int:
        original_turn = board.turn
        board.turn = color
        try:
            score = 0
            for move in board.legal_moves:
                piece = board.piece_at(move.from_square)
                if piece is not None:
                    score += MOBILITY_WEIGHTS.get(piece.piece_type, 0)
            return score
        finally:
            board.turn = original_turn

    def _evaluate_king_safety(self, board: chess.Board) -> int:
        return self._king_safety_for_color(board, chess.WHITE) - self._king_safety_for_color(board, chess.BLACK)

    def _king_safety_for_color(self, board: chess.Board, color: chess.Color) -> int:
        king_square = board.king(color)
        if king_square is None:
            return 0

        pressure = len(board.attackers(not color, king_square)) * 18
        shield = 0
        forward = 1 if color == chess.WHITE else -1
        king_file = chess.square_file(king_square)
        king_rank = chess.square_rank(king_square)

        for file_index in range(max(0, king_file - 1), min(7, king_file + 1) + 1):
            candidate_rank = king_rank + forward
            if 0 <= candidate_rank <= 7:
                candidate_square = chess.square(file_index, candidate_rank)
                piece = board.piece_at(candidate_square)
                if piece is not None and piece.color == color and piece.piece_type == chess.PAWN:
                    shield += 10
        return shield - pressure


__all__ = ["BoardEvaluator", "PIECE_VALUES"]
