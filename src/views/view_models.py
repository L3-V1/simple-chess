from __future__ import annotations

from dataclasses import dataclass

import chess
import pygame

from src.core import EloRating


@dataclass(frozen=True)
class RatingSlider:
    rect: pygame.Rect
    knob_radius: int


@dataclass(frozen=True)
class ColorButton:
    color: chess.Color
    rect: pygame.Rect


@dataclass(frozen=True)
class ActionButton:
    label: str
    rect: pygame.Rect
