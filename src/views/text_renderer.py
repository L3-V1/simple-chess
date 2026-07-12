from __future__ import annotations

import math
from dataclasses import dataclass

import pygame
import pygame.freetype


@dataclass(frozen=True)
class UiFont:
    font: pygame.freetype.Font
    render_scale: int

    def measure_width(self, text: str) -> int:
        """Return the display width of text after downsampling."""
        width = self.font.get_rect(text).width
        return math.ceil(width / self.render_scale)


class TextRenderer:
    def __init__(self, default_color: tuple[int, int, int]) -> None:
        self._default_color = default_color
        self.title_font = self._load_font(size=30, bold=True)
        self.body_font = self._load_font(size=24)
        self.small_font = self._load_font(size=20)

    def render(
        self,
        font: UiFont,
        text: str,
        color: tuple[int, int, int] | None = None,
    ) -> pygame.Surface:
        rendered_surface, _ = font.font.render(text, fgcolor=color or self._default_color)
        final_surface = self._downsample_surface(rendered_surface, font.render_scale)
        return final_surface.convert_alpha() if pygame.display.get_surface() is not None else final_surface

    def wrap(
        self,
        surface: pygame.Surface,
        font: UiFont,
        text: str,
        color: tuple[int, int, int],
        left: int,
        top: int,
        max_width: int,
        line_height: int,
    ) -> int:
        words = text.split()
        current_line = ""
        current_top = top

        for word in words:
            candidate = word if not current_line else f"{current_line} {word}"
            if font.measure_width(candidate) <= max_width:
                current_line = candidate
                continue
            if current_line:
                line_surface = self.render(font, current_line, color)
                surface.blit(line_surface, (left, current_top))
                current_top += line_height
            current_line = word

        if current_line:
            line_surface = self.render(font, current_line, color)
            surface.blit(line_surface, (left, current_top))
            current_top += line_height

        return current_top

    def _load_font(self, size: int, bold: bool = False) -> UiFont:
        render_scale = 2
        font_path = self._find_font_path()
        font = pygame.freetype.Font(font_path, size * render_scale)
        font.pad = False
        font.kerning = True
        font.origin = False
        font.strong = bold
        font.ucs4 = True
        font.style = pygame.freetype.STYLE_STRONG if bold else pygame.freetype.STYLE_DEFAULT
        return UiFont(font=font, render_scale=render_scale)

    def _find_font_path(self) -> str | None:
        preferred_fonts = (
            "Aptos",
            "Segoe UI Variable",
            "Bahnschrift",
            "Segoe UI",
            "Trebuchet MS",
            "Verdana",
        )
        for font_name in preferred_fonts:
            font_path = pygame.font.match_font(font_name)
            if font_path is not None:
                return font_path
        return None

    def _downsample_surface(self, surface: pygame.Surface, render_scale: int) -> pygame.Surface:
        if render_scale <= 1:
            return surface

        target_width = max(1, round(surface.get_width() / render_scale))
        target_height = max(1, round(surface.get_height() / render_scale))
        return pygame.transform.smoothscale(surface, (target_width, target_height))
