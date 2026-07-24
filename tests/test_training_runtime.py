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


def test_training_runtime_preloads_selected_name_for_editing() -> None:
    opening = OpeningLine(
        name="Caro-Kann",
        player_color=chess.BLACK,
        moves_uci=("e2e4", "c7c6"),
    )
    runtime = TrainingRuntime()

    runtime.begin_name_edit(opening)

    assert runtime.opening_name_input == "Caro-Kann"
    assert runtime.active_input == "name"
    assert runtime.is_editing_name is True
    assert "edite o nome" in runtime.feedback_message.lower()


def test_training_runtime_finishes_name_edit_by_clearing_input() -> None:
    runtime = TrainingRuntime(
        opening_name_input="Nome temporário",
        active_input="name",
        is_editing_name=True,
    )

    runtime.finish_name_edit()

    assert runtime.opening_name_input == ""
    assert runtime.active_input is None
    assert runtime.is_editing_name is False
