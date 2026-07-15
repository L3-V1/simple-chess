from __future__ import annotations

import json
import re
from dataclasses import dataclass
from pathlib import Path

import chess

from src.models.opening_line import OpeningLine


@dataclass
class OpeningCatalog:
    """Persist and validate opening lines for training mode."""

    storage_path: Path

    def load_openings(self) -> list[OpeningLine]:
        """Load all stored openings from disk."""
        if not self.storage_path.exists():
            return []
        with self.storage_path.open("r", encoding="utf-8") as file:
            data = json.load(file)
        return [OpeningLine.from_dict(item) for item in data]

    def add_opening(
        self,
        name: str,
        player_color: chess.Color,
        moves_text: str,
    ) -> OpeningLine:
        """Validate and persist a new opening line."""
        cleaned_name = name.strip()
        if not cleaned_name:
            raise ValueError("Informe um nome para a abertura.")

        openings = self.load_openings()
        if any(opening.name.lower() == cleaned_name.lower() for opening in openings):
            raise ValueError("Já existe uma abertura cadastrada com esse nome.")

        moves_uci = self._parse_moves(moves_text)
        opening = OpeningLine(
            name=cleaned_name,
            player_color=player_color,
            moves_uci=moves_uci,
        )
        if not self._line_contains_player_move(opening):
            raise ValueError("Cadastre ao menos um lance do lado que será treinado.")

        openings.append(opening)
        self._save_openings(openings)
        return opening

    def delete_opening(self, name: str) -> None:
        """Remove a stored opening by name."""
        openings = self.load_openings()
        filtered_openings = [opening for opening in openings if opening.name != name]
        if len(filtered_openings) == len(openings):
            raise ValueError("Abertura não encontrada para exclusão.")
        self._save_openings(filtered_openings)

    def _parse_moves(self, moves_text: str) -> tuple[str, ...]:
        normalized_text = re.sub(r"\d+\.(\.\.)?", " ", moves_text)
        tokens = [
            token
            for token in normalized_text.replace("\n", " ").split()
            if token not in {"1-0", "0-1", "1/2-1/2", "*"}
        ]
        if not tokens:
            raise ValueError("Informe a sequência de lances da abertura.")

        board = chess.Board()
        moves_uci: list[str] = []
        for token in tokens:
            try:
                move = board.parse_san(token)
            except ValueError as error:
                raise ValueError(f"Lance inválido na abertura: {token}") from error
            moves_uci.append(move.uci())
            board.push(move)
        return tuple(moves_uci)

    def _line_contains_player_move(self, opening: OpeningLine) -> bool:
        player_starts_at = 0 if opening.player_color == chess.WHITE else 1
        return player_starts_at < len(opening.moves_uci)

    def _save_openings(self, openings: list[OpeningLine]) -> None:
        self.storage_path.parent.mkdir(parents=True, exist_ok=True)
        data = [opening.to_dict() for opening in openings]
        with self.storage_path.open("w", encoding="utf-8") as file:
            json.dump(data, file, ensure_ascii=False, indent=2)
