from __future__ import annotations

from enum import Enum


class TrainingMoveFeedback(str, Enum):
    """Represent the outcome of the last training move attempt."""

    NONE = "none"
    CORRECT = "correct"
    INCORRECT = "incorrect"
