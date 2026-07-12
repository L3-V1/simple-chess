from __future__ import annotations

import random
from dataclasses import dataclass, field

import chess

from core import AI_PROFILES, AiProfile, EloRating
from services.evaluation import BoardEvaluator, PIECE_VALUES
from services.opening_book import choose_opening_move
from services.search_engine import MinimaxSearchEngine


@dataclass
class ComputerPlayer:
    rating: EloRating
    random_generator: random.Random = field(default_factory=random.Random)
    search_engine: MinimaxSearchEngine = field(init=False)

    def __post_init__(self) -> None:
        self.search_engine = MinimaxSearchEngine(random_generator=self.random_generator)

    def choose_move(self, board: chess.Board) -> chess.Move:
        """Choose a legal move based on the configured rating profile."""
        legal_moves = list(board.legal_moves)
        if not legal_moves:
            raise ValueError("No legal moves available for the computer player.")

        opening_move = choose_opening_move(board, self.rating, self.random_generator)
        if opening_move is not None:
            return opening_move

        profile = AI_PROFILES[self.rating]
        if profile.depth <= 1 and profile.random_move_bias >= 0.5:
            return self._choose_easy_move(board, legal_moves, profile)

        evaluator = BoardEvaluator(profile)
        return self.search_engine.choose_move(board, evaluator, profile)

    def _choose_easy_move(
        self,
        board: chess.Board,
        legal_moves: list[chess.Move],
        profile: AiProfile,
    ) -> chess.Move:
        tactical_moves = self._rank_tactical_moves(board, legal_moves)
        if tactical_moves and self.random_generator.random() > profile.random_move_bias:
            return tactical_moves[0]
        if tactical_moves and self.random_generator.random() < 0.45:
            return self.random_generator.choice(tactical_moves[: min(3, len(tactical_moves))])
        return self.random_generator.choice(legal_moves)

    def _rank_tactical_moves(self, board: chess.Board, legal_moves: list[chess.Move]) -> list[chess.Move]:
        scored_moves: list[tuple[int, chess.Move]] = []
        for move in legal_moves:
            score = 0
            if board.is_capture(move):
                score += self._capture_score(board, move)
            if board.gives_check(move):
                score += 50
            if move.promotion:
                score += PIECE_VALUES.get(move.promotion, 0)
            if score > 0:
                scored_moves.append((score, move))
        scored_moves.sort(key=lambda item: item[0], reverse=True)
        return [move for _, move in scored_moves]

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
