import chess

from src.models import GameSession


def test_game_session_selects_and_applies_pawn_move() -> None:
    session = GameSession()

    moved = session.handle_player_click(chess.E2)
    assert moved is False
    assert chess.E4 in session.legal_targets

    moved = session.handle_player_click(chess.E4)
    assert moved is True
    assert session.board.piece_at(chess.E4) is not None
    assert session.board.turn == chess.BLACK


def test_game_session_requires_promotion_choice() -> None:
    session = GameSession(board=chess.Board("4k3/P7/8/8/8/8/8/4K3 w - - 0 1"))

    moved = session.handle_player_click(chess.A7)
    assert moved is False

    moved = session.handle_player_click(chess.A8)
    assert moved is False
    assert session.pending_promotion == (chess.A7, chess.A8)

    promoted = session.choose_promotion(chess.QUEEN)
    assert promoted is True
    piece = session.board.piece_at(chess.A8)
    assert piece is not None
    assert piece.piece_type == chess.QUEEN


def test_game_session_allows_resignation() -> None:
    session = GameSession()

    session.resign(chess.WHITE)

    assert session.is_finished() is True
    assert session.resigned_color == chess.WHITE
    assert "desist" in session.status_message().lower()


def test_game_session_reset_clears_resignation_state() -> None:
    session = GameSession()
    session.resign(chess.WHITE)

    session.reset()

    assert session.is_finished() is False
    assert session.resigned_color is None


def test_game_session_marks_capture_for_audio_feedback() -> None:
    session = GameSession(board=chess.Board("4k3/8/8/3p4/4P3/8/8/4K3 w - - 0 1"))

    moved = session.handle_player_click(chess.E4)
    assert moved is False

    moved = session.handle_player_click(chess.D5)

    assert moved is True
    assert session.last_move_was_capture is True
    assert session.last_move_was_castling is False


def test_game_session_marks_castling_for_audio_feedback() -> None:
    session = GameSession(board=chess.Board("4k2r/8/8/8/8/8/8/4K2R w Kk - 0 1"))

    moved = session.handle_player_click(chess.E1)
    assert moved is False

    moved = session.handle_player_click(chess.G1)

    assert moved is True
    assert session.last_move_was_capture is False
    assert session.last_move_was_castling is True
