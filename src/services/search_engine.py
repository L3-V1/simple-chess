from __future__ import annotations

import math
import random
import time
from dataclasses import dataclass, field

import chess

from src.core import AiProfile
from src.services.evaluation import BoardEvaluator
from src.services.evaluation_tables import PIECE_VALUES


class SearchTimeout(Exception):
    """Raised when the AI search exceeds the allotted think time."""


@dataclass
class MinimaxSearchEngine:
    random_generator: random.Random
    transposition_table: dict[tuple[object, int, bool], float] = field(default_factory=dict)

    def choose_move(
        self,
        board: chess.Board,
        evaluator: BoardEvaluator,
        profile: AiProfile,
    ) -> chess.Move:
        """Select the best move with iterative deepening and alpha-beta pruning."""
        self.transposition_table.clear()
        maximizing_color = board.turn
        ordered_moves = self._order_moves(board, list(board.legal_moves))
        fallback_move = ordered_moves[0]
        if profile.max_search_time_seconds <= 0:
            return self._search_best_move(
                board=board,
                evaluator=evaluator,
                depth=profile.depth,
                maximizing_color=maximizing_color,
                deadline=None,
                quiescence_depth=profile.quiescence_depth,
            )

        deadline = time.perf_counter() + profile.max_search_time_seconds
        best_move = fallback_move
        for depth in range(1, profile.depth + 1):
            try:
                best_move = self._search_best_move(
                    board=board,
                    evaluator=evaluator,
                    depth=depth,
                    maximizing_color=maximizing_color,
                    deadline=deadline,
                    quiescence_depth=profile.quiescence_depth,
                )
            except SearchTimeout:
                break
        return best_move

    def _search_best_move(
        self,
        board: chess.Board,
        evaluator: BoardEvaluator,
        depth: int,
        maximizing_color: chess.Color,
        deadline: float | None,
        quiescence_depth: int,
    ) -> chess.Move:
        best_value = -math.inf
        best_moves: list[chess.Move] = []
        ordered_moves = self._order_moves(board, list(board.legal_moves))
        mating_moves: list[chess.Move] = []

        for move in ordered_moves:
            self._ensure_time_available(deadline)
            board.push(move)
            if board.is_checkmate():
                mating_moves.append(move)
                board.pop()
                continue
            value = self._minimax(
                board=board,
                depth=depth - 1,
                alpha=-math.inf,
                beta=math.inf,
                maximizing=False,
                maximizing_color=maximizing_color,
                evaluator=evaluator,
                deadline=deadline,
                quiescence_depth=quiescence_depth,
            )
            board.pop()
            if value > best_value:
                best_value = value
                best_moves = [move]
            elif value == best_value:
                best_moves.append(move)

        if mating_moves:
            return self.random_generator.choice(mating_moves)
        return self.random_generator.choice(best_moves or ordered_moves[:1])

    def _minimax(
        self,
        board: chess.Board,
        depth: int,
        alpha: float,
        beta: float,
        maximizing: bool,
        maximizing_color: chess.Color,
        evaluator: BoardEvaluator,
        deadline: float | None,
        quiescence_depth: int,
    ) -> float:
        self._ensure_time_available(deadline)
        if board.is_game_over(claim_draw=True):
            return evaluator.evaluate(board, maximizing_color)
        if depth == 0:
            return self._quiescence_search(
                board=board,
                alpha=alpha,
                beta=beta,
                maximizing=maximizing,
                maximizing_color=maximizing_color,
                evaluator=evaluator,
                deadline=deadline,
                depth=quiescence_depth,
            )

        table_key = (self._position_key(board), depth, maximizing)
        cached_value = self.transposition_table.get(table_key)
        if cached_value is not None:
            return cached_value

        ordered_moves = self._order_moves(board, list(board.legal_moves))
        if maximizing:
            return self._maximize(
                board=board,
                moves=ordered_moves,
                depth=depth,
                alpha=alpha,
                beta=beta,
                maximizing_color=maximizing_color,
                evaluator=evaluator,
                deadline=deadline,
                quiescence_depth=quiescence_depth,
                table_key=table_key,
            )
        return self._minimize(
            board=board,
            moves=ordered_moves,
            depth=depth,
            alpha=alpha,
            beta=beta,
            maximizing_color=maximizing_color,
            evaluator=evaluator,
            deadline=deadline,
            quiescence_depth=quiescence_depth,
            table_key=table_key,
        )

    def _maximize(
        self,
        board: chess.Board,
        moves: list[chess.Move],
        depth: int,
        alpha: float,
        beta: float,
        maximizing_color: chess.Color,
        evaluator: BoardEvaluator,
        deadline: float | None,
        quiescence_depth: int,
        table_key: tuple[object, int, bool],
    ) -> float:
        value = -math.inf
        for move in moves:
            board.push(move)
            value = max(
                value,
                self._minimax(
                    board,
                    depth - 1,
                    alpha,
                    beta,
                    False,
                    maximizing_color,
                    evaluator,
                    deadline,
                    quiescence_depth,
                ),
            )
            board.pop()
            alpha = max(alpha, value)
            if beta <= alpha:
                break
        self.transposition_table[table_key] = value
        return value

    def _minimize(
        self,
        board: chess.Board,
        moves: list[chess.Move],
        depth: int,
        alpha: float,
        beta: float,
        maximizing_color: chess.Color,
        evaluator: BoardEvaluator,
        deadline: float | None,
        quiescence_depth: int,
        table_key: tuple[object, int, bool],
    ) -> float:
        value = math.inf
        for move in moves:
            board.push(move)
            value = min(
                value,
                self._minimax(
                    board,
                    depth - 1,
                    alpha,
                    beta,
                    True,
                    maximizing_color,
                    evaluator,
                    deadline,
                    quiescence_depth,
                ),
            )
            board.pop()
            beta = min(beta, value)
            if beta <= alpha:
                break
        self.transposition_table[table_key] = value
        return value

    def _quiescence_search(
        self,
        board: chess.Board,
        alpha: float,
        beta: float,
        maximizing: bool,
        maximizing_color: chess.Color,
        evaluator: BoardEvaluator,
        deadline: float | None,
        depth: int,
    ) -> float:
        self._ensure_time_available(deadline)
        stand_pat = evaluator.evaluate(board, maximizing_color)
        if depth == 0:
            return stand_pat

        if maximizing:
            if stand_pat >= beta:
                return stand_pat
            alpha = max(alpha, stand_pat)
            return self._quiescence_max(
                board,
                alpha,
                beta,
                maximizing_color,
                evaluator,
                deadline,
                depth,
                stand_pat,
            )

        if stand_pat <= alpha:
            return stand_pat
        beta = min(beta, stand_pat)
        return self._quiescence_min(
            board,
            alpha,
            beta,
            maximizing_color,
            evaluator,
            deadline,
            depth,
            stand_pat,
        )

    def _quiescence_max(
        self,
        board: chess.Board,
        alpha: float,
        beta: float,
        maximizing_color: chess.Color,
        evaluator: BoardEvaluator,
        deadline: float | None,
        depth: int,
        current_value: float,
    ) -> float:
        tactical_moves = self._tactical_moves(board)
        if not tactical_moves:
            return current_value

        value = current_value
        for move in tactical_moves:
            board.push(move)
            value = max(
                value,
                self._quiescence_search(
                    board,
                    alpha,
                    beta,
                    False,
                    maximizing_color,
                    evaluator,
                    deadline,
                    depth - 1,
                ),
            )
            board.pop()
            alpha = max(alpha, value)
            if alpha >= beta:
                break
        return value

    def _quiescence_min(
        self,
        board: chess.Board,
        alpha: float,
        beta: float,
        maximizing_color: chess.Color,
        evaluator: BoardEvaluator,
        deadline: float | None,
        depth: int,
        current_value: float,
    ) -> float:
        tactical_moves = self._tactical_moves(board)
        if not tactical_moves:
            return current_value

        value = current_value
        for move in tactical_moves:
            board.push(move)
            value = min(
                value,
                self._quiescence_search(
                    board,
                    alpha,
                    beta,
                    True,
                    maximizing_color,
                    evaluator,
                    deadline,
                    depth - 1,
                ),
            )
            board.pop()
            beta = min(beta, value)
            if alpha >= beta:
                break
        return value

    def _order_moves(self, board: chess.Board, legal_moves: list[chess.Move]) -> list[chess.Move]:
        return sorted(legal_moves, key=lambda move: self._move_order_score(board, move), reverse=True)

    def _tactical_moves(self, board: chess.Board) -> list[chess.Move]:
        tactical_moves = [
            move
            for move in board.legal_moves
            if board.is_capture(move) or board.gives_check(move) or move.promotion
        ]
        return self._order_moves(board, tactical_moves)

    def _move_order_score(self, board: chess.Board, move: chess.Move) -> int:
        score = 0
        if board.is_capture(move):
            score += 200 + self._capture_score(board, move)
        if board.gives_check(move):
            score += 100
        if move.promotion:
            score += PIECE_VALUES.get(move.promotion, 0)
        return score

    def _capture_score(self, board: chess.Board, move: chess.Move) -> int:
        attacking_piece = board.piece_at(move.from_square)
        victim_square = move.to_square if not board.is_en_passant(move) else chess.square(
            chess.square_file(move.to_square),
            chess.square_rank(move.from_square),
        )
        victim_piece = board.piece_at(victim_square)
        if attacking_piece is None or victim_piece is None:
            return 0
        return PIECE_VALUES[victim_piece.piece_type] - PIECE_VALUES[attacking_piece.piece_type] // 10

    def _ensure_time_available(self, deadline: float | None) -> None:
        if deadline is not None and time.perf_counter() >= deadline:
            raise SearchTimeout

    def _position_key(self, board: chess.Board) -> object:
        if hasattr(board, "_transposition_key"):
            return board._transposition_key()
        return board.fen()
