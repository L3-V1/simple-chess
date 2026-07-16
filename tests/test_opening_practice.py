import chess

from src.models import OpeningLine, OpeningPracticeSession, TrainingMoveFeedback


def test_opening_practice_rejects_wrong_player_move() -> None:
    opening = OpeningLine(
        name="Italiano",
        player_color=chess.WHITE,
        moves_uci=("e2e4", "e7e5", "g1f3", "b8c6"),
    )
    practice = OpeningPracticeSession(opening)
    practice.start()

    moved = practice.handle_player_click(chess.D2)
    assert moved is False

    moved = practice.handle_player_click(chess.D4)

    assert moved is False
    assert "abertura treinada" in practice.session.move_error_message.lower()
    assert practice.current_move_index == 0
    assert practice.last_feedback == TrainingMoveFeedback.INCORRECT


def test_opening_practice_advances_opponent_moves_automatically_for_black() -> None:
    opening = OpeningLine(
        name="Siciliana",
        player_color=chess.BLACK,
        moves_uci=("e2e4", "c7c5", "g1f3", "d7d6"),
    )
    practice = OpeningPracticeSession(opening)

    practice.start()

    assert practice.current_move_index == 1
    assert practice.session.board.turn == chess.BLACK

    moved = practice.handle_player_click(chess.C7)
    assert moved is False

    moved = practice.handle_player_click(chess.C5)

    assert moved is True
    assert practice.current_move_index == 3
    assert practice.session.board.turn == chess.BLACK
    assert practice.last_feedback == TrainingMoveFeedback.CORRECT
