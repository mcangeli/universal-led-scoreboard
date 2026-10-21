"""Monotonic, non-blocking redraw cadence for background Bullpen screens."""
from __future__ import annotations

import math
import time


class BullpenCadence:
    """Track the next eligible redraw without sleeping on the display thread."""

    def __init__(self, interval: float, *, start: float | None = None):
        if isinstance(interval, bool) or not isinstance(interval, (int, float)):
            raise ValueError("interval must be numeric")
        self.interval = float(interval)
        if not math.isfinite(self.interval) or self.interval <= 0:
            raise ValueError("interval must be positive and finite")
        self._next = (time.monotonic() if start is None else float(start)) + self.interval

    def due(self, now: float | None = None) -> bool:
        now = time.monotonic() if now is None else float(now)
        if not math.isfinite(now):
            raise ValueError("now must be finite")
        return now >= self._next

    def advance(self, now: float | None = None) -> None:
        """Advance one deadline, dropping missed ticks instead of burst redraws."""
        now = time.monotonic() if now is None else float(now)
        if not math.isfinite(now):
            raise ValueError("now must be finite")
        self._next = max(self._next + self.interval, now + self.interval)

    def reset(self, now: float | None = None) -> None:
        now = time.monotonic() if now is None else float(now)
        if not math.isfinite(now):
            raise ValueError("now must be finite")
        self._next = now + self.interval
