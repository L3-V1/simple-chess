from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path

import pygame


@dataclass
class SoundManager:
    """Load and play UI sounds without breaking the app when audio is unavailable."""

    move_sound_path: Path
    _move_sound: pygame.mixer.Sound | None = field(default=None, init=False)
    _enabled: bool = field(default=False, init=False)

    def initialize(self) -> None:
        """Initialize pygame mixer and preload move sound if possible."""
        try:
            if not pygame.mixer.get_init():
                pygame.mixer.init()
            self._move_sound = pygame.mixer.Sound(str(self.move_sound_path))
            self._move_sound.set_volume(0.55)
            self._enabled = True
        except pygame.error:
            self._enabled = False
            self._move_sound = None

    def play_move(self) -> None:
        """Play the wooden move sound when available."""
        if not self._enabled or self._move_sound is None:
            return
        self._move_sound.play()
