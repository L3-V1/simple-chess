from __future__ import annotations

from enum import Enum


class AppScreen(str, Enum):
    """Represent the current top-level screen shown by the application."""

    MENU = "menu"
    GAME = "game"
    TRAINING = "training"
