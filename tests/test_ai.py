import chess
import random

from src.core import AI_PROFILES, ELO_RATINGS, EloRating
from src.services import BoardEvaluator, ComputerPlayer


def test_supported_elo_ratings_cover_500_to_2500_in_steps_of_500() -> None:
    assert [int(rating) for rating in ELO_RATINGS] == [500, 1000, 1500, 2000, 2500]


def test_elo_500_ai_always_returns_legal_move() -> None:
    board = chess.Board()
    player = ComputerPlayer(EloRating.ELO_500)

    move = player.choose_move(board)

    assert move in board.legal_moves


def test_opening_book_adds_variety_to_initial_choices() -> None:
    board = chess.Board()
    choices = {
        ComputerPlayer(EloRating.ELO_1500, random_generator=random.Random(seed)).choose_move(board).uci()
        for seed in range(8)
    }

    assert len(choices) >= 2
    assert choices <= {"e2e4", "d2d4", "c2c4", "g1f3"}


def test_opening_book_responds_theoretically_to_e4() -> None:
    board = chess.Board()
    board.push_uci("e2e4")

    move = ComputerPlayer(EloRating.ELO_2000, random_generator=random.Random(3)).choose_move(board)

    assert move.uci() in {"e7e5", "c7c5", "e7e6", "c7c6", "d7d6"}


def test_elo_1500_ai_finds_forced_checkmate_in_one() -> None:
    board = chess.Board("k7/7Q/K7/8/8/8/8/8 w - - 0 1")
    player = ComputerPlayer(EloRating.ELO_1500)

    move = player.choose_move(board)
    board.push(move)

    assert board.is_checkmate()


def test_elo_2500_evaluation_rewards_center_control() -> None:
    central_board = chess.Board("4k3/8/8/3N4/8/8/P7/4K3 w - - 0 1")
    edge_board = chess.Board("4k3/8/8/N7/8/8/P7/4K3 w - - 0 1")
    evaluator = BoardEvaluator(profile=AI_PROFILES[EloRating.ELO_2500])

    central_score = evaluator.evaluate(central_board, chess.WHITE)
    edge_score = evaluator.evaluate(edge_board, chess.WHITE)

    assert central_score > edge_score
