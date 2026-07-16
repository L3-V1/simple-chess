import pygame

from src.views.text_renderer import TextRenderer


def test_text_renderer_fit_to_width_preserves_short_text() -> None:
    pygame.init()
    try:
        renderer = TextRenderer(default_color=(255, 255, 255))
        font = renderer.small_font
        text = "Brancas: e4 e5"

        fitted = renderer.fit_to_width(font, text, font.measure_width(text) + 4)

        assert fitted == text
    finally:
        pygame.quit()


def test_text_renderer_fit_to_width_adds_ellipsis_for_long_text() -> None:
    pygame.init()
    try:
        renderer = TextRenderer(default_color=(255, 255, 255))
        font = renderer.small_font
        text = "Brancas: e4 e5 Nf3 Nc6 Bc4 Bc5 c3 Nf6 d4 exd4"
        max_width = font.measure_width("Brancas: e4 e5 Nf3")

        fitted = renderer.fit_to_width(font, text, max_width)

        assert fitted.endswith("...")
        assert font.measure_width(fitted) <= max_width
    finally:
        pygame.quit()
