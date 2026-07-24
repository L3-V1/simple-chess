from __future__ import annotations

from dataclasses import dataclass, field

import chess

from .opening_line import OpeningLine
from .opening_practice_session import OpeningPracticeSession


@dataclass
class TrainingRuntime:
    """Store mutable state for the opening training screen."""

    openings: list[OpeningLine] = field(default_factory=list)
    selected_opening_name: str | None = None
    opening_name_input: str = ""
    opening_moves_input: str = ""
    opening_color: chess.Color = chess.WHITE
    active_input: str | None = None
    feedback_message: str = ""
    practice_session: OpeningPracticeSession | None = None
    is_editing_name: bool = False

    def set_openings(self, openings: list[OpeningLine]) -> None:
        """Replace the stored opening list and keep a valid selection."""
        self.openings = openings
        if not openings:
            self.selected_opening_name = None
            return
        if self.selected_opening_name not in {opening.name for opening in openings}:
            self.selected_opening_name = openings[0].name

    def select_opening(self, opening_name: str) -> bool:
        """Select an opening by name and report whether the selection changed."""
        selection_changed = self.selected_opening_name != opening_name
        self.selected_opening_name = opening_name
        self.opening_name_input = ""
        self.is_editing_name = False
        self.feedback_message = ""
        return selection_changed

    def selected_opening(self) -> OpeningLine | None:
        """Return the currently selected opening, if any."""
        for opening in self.openings:
            if opening.name == self.selected_opening_name:
                return opening
        return None

    def clear_form(self) -> None:
        """Reset the opening creation form."""
        self.opening_name_input = ""
        self.opening_moves_input = ""
        self.opening_color = chess.WHITE
        self.active_input = None
        self.is_editing_name = False

    def begin_name_edit(self, opening: OpeningLine) -> None:
        """Preload the selected opening name into the edit form."""
        self.opening_name_input = opening.name
        self.active_input = "name"
        self.is_editing_name = True
        self.feedback_message = "Edite o nome e clique novamente em Editar nome."

    def finish_name_edit(self) -> None:
        """Leave name editing mode and clear the name input field."""
        self.opening_name_input = ""
        self.active_input = None
        self.is_editing_name = False

    def begin_practice(self, opening: OpeningLine) -> None:
        """Start a practice session for the selected opening."""
        self.practice_session = OpeningPracticeSession(opening=opening)
        self.practice_session.start()
        self.feedback_message = ""

    def end_practice(self) -> None:
        """Leave the active practice session."""
        self.practice_session = None
        self.feedback_message = ""
