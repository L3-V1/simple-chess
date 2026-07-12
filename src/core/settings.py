from __future__ import annotations

from dataclasses import dataclass
from enum import IntEnum


class EloRating(IntEnum):
    ELO_500 = 500
    ELO_1000 = 1000
    ELO_1500 = 1500
    ELO_2000 = 2000
    ELO_2500 = 2500

    @property
    def label(self) -> str:
        return str(int(self))


@dataclass(frozen=True)
class AiProfile:
    depth: int
    random_move_bias: float
    use_piece_square_tables: bool
    use_center_control: bool
    max_search_time_seconds: float
    quiescence_depth: int


@dataclass(frozen=True)
class ColorPalette:
    light_square: tuple[int, int, int]
    dark_square: tuple[int, int, int]
    background: tuple[int, int, int]
    panel: tuple[int, int, int]
    text: tuple[int, int, int]
    accent: tuple[int, int, int]
    highlight: tuple[int, int, int]
    legal_move: tuple[int, int, int]
    capture_move: tuple[int, int, int]
    danger: tuple[int, int, int]


@dataclass(frozen=True)
class DisplaySettings:
    board_size: int = 640
    side_panel_width: int = 260
    window_height: int = 640
    fps: int = 60

    @property
    def window_width(self) -> int:
        return self.board_size + self.side_panel_width

    @property
    def square_size(self) -> int:
        return self.board_size // 8


DISPLAY_SETTINGS = DisplaySettings()

COLOR_PALETTE = ColorPalette(
    light_square=(228, 238, 224),
    dark_square=(110, 146, 102),
    background=(28, 77, 55),
    panel=(244, 249, 241),
    text=(27, 62, 44),
    accent=(71, 130, 92),
    highlight=(188, 214, 154),
    legal_move=(36, 96, 72),
    capture_move=(214, 122, 88),
    danger=(180, 77, 77),
)

ELO_RATINGS = tuple(EloRating)

AI_PROFILES: dict[EloRating, AiProfile] = {
    EloRating.ELO_500: AiProfile(
        depth=1,
        random_move_bias=0.72,
        use_piece_square_tables=False,
        use_center_control=False,
        max_search_time_seconds=0.0,
        quiescence_depth=0,
    ),
    EloRating.ELO_1000: AiProfile(
        depth=2,
        random_move_bias=0.35,
        use_piece_square_tables=True,
        use_center_control=False,
        max_search_time_seconds=0.12,
        quiescence_depth=1,
    ),
    EloRating.ELO_1500: AiProfile(
        depth=3,
        random_move_bias=0.1,
        use_piece_square_tables=True,
        use_center_control=True,
        max_search_time_seconds=0.38,
        quiescence_depth=3,
    ),
    EloRating.ELO_2000: AiProfile(
        depth=4,
        random_move_bias=0.0,
        use_piece_square_tables=True,
        use_center_control=True,
        max_search_time_seconds=0.8,
        quiescence_depth=5,
    ),
    EloRating.ELO_2500: AiProfile(
        depth=4,
        random_move_bias=0.0,
        use_piece_square_tables=True,
        use_center_control=True,
        max_search_time_seconds=1.3,
        quiescence_depth=6,
    ),
}
