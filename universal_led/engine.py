"""Time-based screen selection with an initial splash phase."""
from __future__ import annotations
import time
from dataclasses import dataclass, field
from .display import Framebuffer
from .screens import ScreenPlugin, SplashScreen

@dataclass
class ScoreboardEngine:
    screens: list[ScreenPlugin]
    seconds_per_screen: float = 10.0
    splash_seconds: float = 3.0
    clock: callable = time.monotonic
    started: float = field(init=False)
    def __post_init__(self):
        if not self.screens:
            raise ValueError('At least one screen is required')
        if self.seconds_per_screen <= 0 or self.splash_seconds < 0:
            raise ValueError('Invalid screen duration')
        self.started = self.clock()
    def current_screen(self) -> ScreenPlugin:
        elapsed = max(0.0, self.clock() - self.started)
        if elapsed < self.splash_seconds:
            return SplashScreen()
        index = int((elapsed - self.splash_seconds) // self.seconds_per_screen)
        return self.screens[index % len(self.screens)]
    def frame(self) -> Framebuffer:
        return self.current_screen().render()
