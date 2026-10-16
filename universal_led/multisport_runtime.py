"""Shared MLB/NHL frame rotation, preserving the MLB supplemental rotation."""
from __future__ import annotations

import threading
import time


class MultiSportRenderer:
    """Route cached frames without network access; retain legacy single-sport mode."""

    def __init__(self, mlb_renderer, nhl_renderer, active_sport="mlb", clock=time.monotonic):
        self.mlb = mlb_renderer
        self.nhl = nhl_renderer
        self.clock = clock
        self._lock = threading.Lock()
        self._active = "mlb"
        self._enabled = ("mlb",)
        self._interval = 12
        self._started = clock()
        self.set_active_sport(active_sport)

    @property
    def active_sport(self):
        with self._lock:
            return self._active

    def set_active_sport(self, sport):
        if sport not in ("mlb", "nhl"):
            raise ValueError("Unsupported active sport")
        with self._lock:
            self._active = sport
            self._enabled = (sport,)
            self._started = self.clock()

    def configure_rotation(self, enabled_sports, interval=12, preferred="mlb"):
        enabled = tuple(s for s in ("mlb", "nhl") if s in enabled_sports)
        if not enabled or preferred not in ("mlb", "nhl"):
            raise ValueError("Invalid sport rotation")
        if type(interval) not in (int, float) or not 1 <= interval <= 3600:
            raise ValueError("Invalid sport rotation interval")
        with self._lock:
            self._enabled = enabled
            self._active = preferred if preferred in enabled else enabled[0]
            self._interval = interval
            self._started = self.clock()

    def _selected(self):
        with self._lock:
            enabled = self._enabled
            if len(enabled) == 1:
                return enabled[0]
            slot = int(max(0, self.clock() - self._started) // self._interval)
            return enabled[slot % len(enabled)]

    def frame(self):
        return (self.nhl if self._selected() == "nhl" else self.mlb).frame()

    def game(self):
        return (self.nhl if self._selected() == "nhl" else self.mlb).game()
