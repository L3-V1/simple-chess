from __future__ import annotations

from dataclasses import dataclass

import pygame

from src.core import ColorPalette, DisplaySettings

from .piece_factory import PieceSpriteFactory
from .text_renderer import TextRenderer, UiFont


@dataclass(frozen=True)
class RenderAssets:
    """Bundle shared rendering dependencies for view components."""

    screen: pygame.Surface
    display_settings: DisplaySettings
    palette: ColorPalette
    square_size: int
    piece_factory: PieceSpriteFactory
    text_renderer: TextRenderer
    title_font: UiFont
    body_font: UiFont
    small_font: UiFont
