from __future__ import annotations

import chess

from src.models import GameSession


def format_move_history(session: GameSession) -> list[str]:
    """Build the last moves shown in the side panel using compact SAN notation."""
    replay_board = session.board.copy(stack=True)
    move_stack = list(replay_board.move_stack)
    while replay_board.move_stack:
        replay_board.pop()

    formatted_moves: list[str] = []
    for move in move_stack:
        formatted_moves.append(normalize_move_notation(replay_board.san(move)))
        replay_board.push(move)
    return formatted_moves[-12:]


def normalize_move_notation(san_move: str) -> str:
    """Convert SAN moves to the compact project display format."""
    normalized_move = san_move.replace("0-0-0", "O-O-O").replace("0-0", "O-O")
    return normalized_move[1:] if normalized_move.startswith("P") else normalized_move
