from pathlib import Path

import chess

from src.services import OpeningCatalog


def test_opening_catalog_saves_and_loads_opening_lines(tmp_path: Path) -> None:
    catalog = OpeningCatalog(tmp_path / "openings.json")

    opening = catalog.add_opening(
        name="Ruy Lopez",
        player_color=chess.WHITE,
        moves_text="1. e4 e5 2. Nf3 Nc6 3. Bb5 a6",
    )
    loaded = catalog.load_openings()

    assert opening.name == "Ruy Lopez"
    assert opening.player_color == chess.WHITE
    assert opening.moves_uci == ("e2e4", "e7e5", "g1f3", "b8c6", "f1b5", "a7a6")
    assert len(loaded) == 1
    assert loaded[0].name == "Ruy Lopez"


def test_opening_catalog_rejects_invalid_move_sequences(tmp_path: Path) -> None:
    catalog = OpeningCatalog(tmp_path / "openings.json")

    try:
        catalog.add_opening(
            name="Linha quebrada",
            player_color=chess.WHITE,
            moves_text="1. e4 e5 2. CavaloX",
        )
    except ValueError as error:
        assert "Lance inválido" in str(error)
    else:
        raise AssertionError("Expected invalid SAN sequence to raise ValueError.")


def test_opening_catalog_deletes_opening_lines(tmp_path: Path) -> None:
    catalog = OpeningCatalog(tmp_path / "openings.json")
    catalog.add_opening(
        name="Francesa",
        player_color=chess.BLACK,
        moves_text="1. e4 e6 2. d4 d5",
    )

    catalog.delete_opening("Francesa")
    loaded = catalog.load_openings()

    assert loaded == []
