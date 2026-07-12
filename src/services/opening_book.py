from __future__ import annotations

import random
from dataclasses import dataclass

import chess

from core import EloRating


@dataclass(frozen=True)
class OpeningChoice:
    move_uci: str
    min_rating: EloRating
    weight: int


OPENING_BOOK: dict[tuple[str, ...], tuple[OpeningChoice, ...]] = {
    (): (
        OpeningChoice("e2e4", EloRating.ELO_500, 36),
        OpeningChoice("d2d4", EloRating.ELO_500, 30),
        OpeningChoice("c2c4", EloRating.ELO_1000, 18),
        OpeningChoice("g1f3", EloRating.ELO_1000, 16),
    ),
    ("e2e4",): (
        OpeningChoice("e7e5", EloRating.ELO_500, 30),
        OpeningChoice("c7c5", EloRating.ELO_1000, 24),
        OpeningChoice("e7e6", EloRating.ELO_1000, 18),
        OpeningChoice("c7c6", EloRating.ELO_1500, 14),
        OpeningChoice("d7d6", EloRating.ELO_1500, 10),
    ),
    ("d2d4",): (
        OpeningChoice("d7d5", EloRating.ELO_500, 34),
        OpeningChoice("g8f6", EloRating.ELO_1000, 24),
        OpeningChoice("e7e6", EloRating.ELO_1000, 18),
    ),
    ("c2c4",): (
        OpeningChoice("e7e5", EloRating.ELO_1000, 24),
        OpeningChoice("g8f6", EloRating.ELO_1000, 26),
        OpeningChoice("c7c5", EloRating.ELO_1500, 16),
        OpeningChoice("e7e6", EloRating.ELO_1500, 14),
    ),
    ("g1f3",): (
        OpeningChoice("d7d5", EloRating.ELO_500, 26),
        OpeningChoice("g8f6", EloRating.ELO_1000, 26),
        OpeningChoice("c7c5", EloRating.ELO_1500, 18),
        OpeningChoice("d7d6", EloRating.ELO_1500, 12),
    ),
    ("e2e4", "e7e5"): (
        OpeningChoice("g1f3", EloRating.ELO_500, 34),
        OpeningChoice("f1c4", EloRating.ELO_500, 20),
        OpeningChoice("b1c3", EloRating.ELO_1000, 16),
        OpeningChoice("f1b5", EloRating.ELO_1500, 24),
    ),
    ("e2e4", "c7c5"): (
        OpeningChoice("g1f3", EloRating.ELO_500, 32),
        OpeningChoice("b1c3", EloRating.ELO_500, 22),
        OpeningChoice("c2c3", EloRating.ELO_1000, 12),
        OpeningChoice("d2d4", EloRating.ELO_1500, 24),
    ),
    ("e2e4", "e7e6"): (
        OpeningChoice("d2d4", EloRating.ELO_500, 34),
        OpeningChoice("b1c3", EloRating.ELO_1000, 20),
        OpeningChoice("g1f3", EloRating.ELO_1000, 18),
    ),
    ("e2e4", "c7c6"): (
        OpeningChoice("d2d4", EloRating.ELO_500, 34),
        OpeningChoice("b1c3", EloRating.ELO_1000, 22),
        OpeningChoice("g1f3", EloRating.ELO_1000, 16),
    ),
    ("d2d4", "d7d5"): (
        OpeningChoice("c2c4", EloRating.ELO_500, 36),
        OpeningChoice("g1f3", EloRating.ELO_500, 20),
        OpeningChoice("e2e3", EloRating.ELO_1000, 14),
    ),
    ("d2d4", "g8f6"): (
        OpeningChoice("c2c4", EloRating.ELO_500, 34),
        OpeningChoice("g1f3", EloRating.ELO_1000, 18),
        OpeningChoice("b1c3", EloRating.ELO_1500, 16),
    ),
    ("c2c4", "e7e5"): (
        OpeningChoice("b1c3", EloRating.ELO_1000, 24),
        OpeningChoice("g2g3", EloRating.ELO_1000, 20),
        OpeningChoice("g1f3", EloRating.ELO_1500, 20),
    ),
    ("c2c4", "g8f6"): (
        OpeningChoice("b1c3", EloRating.ELO_1000, 22),
        OpeningChoice("g2g3", EloRating.ELO_1000, 18),
        OpeningChoice("g1f3", EloRating.ELO_1500, 24),
    ),
    ("e2e4", "e7e5", "g1f3"): (
        OpeningChoice("b8c6", EloRating.ELO_500, 34),
        OpeningChoice("d7d6", EloRating.ELO_1000, 14),
        OpeningChoice("g8f6", EloRating.ELO_1000, 18),
        OpeningChoice("f8c5", EloRating.ELO_1500, 18),
    ),
    ("e2e4", "e7e5", "f1b5"): (
        OpeningChoice("a7a6", EloRating.ELO_1500, 22),
        OpeningChoice("g8f6", EloRating.ELO_1500, 22),
        OpeningChoice("b8c6", EloRating.ELO_1000, 18),
    ),
    ("e2e4", "c7c5", "g1f3"): (
        OpeningChoice("d7d6", EloRating.ELO_500, 26),
        OpeningChoice("b8c6", EloRating.ELO_1000, 20),
        OpeningChoice("e7e6", EloRating.ELO_1000, 18),
        OpeningChoice("g7g6", EloRating.ELO_1500, 12),
    ),
    ("d2d4", "d7d5", "c2c4"): (
        OpeningChoice("e7e6", EloRating.ELO_500, 26),
        OpeningChoice("c7c6", EloRating.ELO_1000, 18),
        OpeningChoice("d5c4", EloRating.ELO_1500, 16),
        OpeningChoice("g8f6", EloRating.ELO_1000, 20),
    ),
}


def choose_opening_move(
    board: chess.Board,
    rating: EloRating,
    random_generator: random.Random,
) -> chess.Move | None:
    """Return a weighted opening move for early positions when available."""
    if len(board.move_stack) > 5:
        return None

    opening_choices = OPENING_BOOK.get(tuple(move.uci() for move in board.move_stack))
    if not opening_choices:
        return None

    legal_moves = {move.uci(): move for move in board.legal_moves}
    weighted_moves: list[chess.Move] = []
    for choice in opening_choices:
        if rating < choice.min_rating:
            continue
        move = legal_moves.get(choice.move_uci)
        if move is not None:
            weighted_moves.extend([move] * choice.weight)

    if not weighted_moves:
        return None
    return random_generator.choice(weighted_moves)

