"""Shared frame selection between MLB and NHL, preserving MLB by default."""
from __future__ import annotations

import threading


class MultiSportRenderer:
    """Thread-safe active sport routing, with no network calls in frame()."""

    def __init__(self, mlb_renderer, nhl_renderer, active_sport="mlb"):
        self.mlb = mlb_renderer
        self.nhl = nhl_renderer
        self._lock = threading.Lock()
        self._active = "mlb"
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

    def frame(self):
        with self._lock:
            sport = self._active
        return (self.nhl if sport == "nhl" else self.mlb).frame()

    def game(self):
        with self._lock:
            sport = self._active
        return (self.nhl if sport == "nhl" else self.mlb).game()
