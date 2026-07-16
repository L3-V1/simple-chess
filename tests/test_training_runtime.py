import chess

from src.models import OpeningLine, TrainingRuntime


def test_training_runtime_reports_opening_selection_changes() -> None:
    runtime = TrainingRuntime(
        openings=[
            OpeningLine(name="Italiana", player_color=chess.WHITE, moves_uci=("e2e4", "e7e5")),
        ],
        selected_opening_name="Italiana",
        feedback_message="Mensagem antiga",
    )

    changed = runtime.select_opening("Siciliana")

    assert changed is True
    assert runtime.selected_opening_name == "Siciliana"
    assert runtime.feedback_message == ""


def test_training_runtime_ignores_same_opening_selection() -> None:
    runtime = TrainingRuntime(
        openings=[
            OpeningLine(name="Francesa", player_color=chess.BLACK, moves_uci=("e2e4", "e7e6")),
        ],
        selected_opening_name="Francesa",
        feedback_message="Mensagem antiga",
    )

    changed = runtime.select_opening("Francesa")

    assert changed is False
    assert runtime.selected_opening_name == "Francesa"
    assert runtime.feedback_message == ""
