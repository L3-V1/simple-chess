from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path

import pygame


class SoundEffect(str, Enum):
    """Enumerate the sound effects used across the application."""

    MOVE = "move"
    CAPTURE = "capture"
    CASTLING = "castling"
    MENU_SELECT = "menu_select"


@dataclass
class SoundManager:
    """Load and play UI sounds without breaking the app when audio is unavailable."""

    sound_paths: dict[SoundEffect, Path]
    _sounds: dict[SoundEffect, pygame.mixer.Sound] = field(default_factory=dict, init=False)
    _enabled: bool = field(default=False, init=False)

    def initialize(self) -> None:
        """Initialize pygame mixer and preload sound effects when possible."""
        try:
            if not pygame.mixer.get_init():
                pygame.mixer.init()
            self._sounds = self._load_sounds()
            self._enabled = bool(self._sounds)
        except pygame.error:
            self._enabled = False
            self._sounds.clear()

    def play(self, effect: SoundEffect) -> None:
        """Play the requested effect when it is available."""
        sound = self._sounds.get(effect)
        if not self._enabled or sound is None:
            return
        sound.play()

    def _load_sounds(self) -> dict[SoundEffect, pygame.mixer.Sound]:
        sounds: dict[SoundEffect, pygame.mixer.Sound] = {}
        for effect, path in self.sound_paths.items():
            sound = self._load_sound(effect, path)
            if sound is not None:
                sounds[effect] = sound
        return sounds

    def _load_sound(
        self,
        effect: SoundEffect,
        path: Path,
    ) -> pygame.mixer.Sound | None:
        try:
            sound = pygame.mixer.Sound(str(path))
            sound.set_volume(self._volume_for_effect(effect))
            return sound
        except (FileNotFoundError, pygame.error):
            return None

    def _volume_for_effect(self, effect: SoundEffect) -> float:
        volumes = {
            SoundEffect.MOVE: 0.55,
            SoundEffect.CAPTURE: 0.65,
            SoundEffect.CASTLING: 0.60,
            SoundEffect.MENU_SELECT: 0.45,
        }
        return volumes[effect]
