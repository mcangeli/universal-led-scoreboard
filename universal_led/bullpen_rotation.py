"""Optional Bullpen slot adapter for existing ULS rotation decisions.

Live-game priority remains owned by the host scheduler. This adapter never
replaces a live game and never blocks waiting for plugin data.
"""
from __future__ import annotations

from .bullpen_background import BullpenBackgroundScreen


class BullpenRotationSlot:
    def __init__(self, background: BullpenBackgroundScreen):
        self.background = background

    def frame(self, *, live_games: bool, selected: bool, now: float | None = None):
        """Return a cached plugin frame only in an eligible non-live slot."""
        if live_games or not selected:
            return None
        self.background.tick(now)
        return self.background.render()
