"""Thread-safe season status snapshot for standings rotation.

Providers update this snapshot outside the frame loop. Failed checks preserve
the last known state; unknown is not silently classified as offseason.
"""
from __future__ import annotations

from threading import Lock

VALID_PHASES = frozenset({'regular', 'postseason', 'offseason'})
UNKNOWN = 'unknown'


class StandingsSeasonStatus:
    def __init__(self):
        self._lock = Lock()
        self._phases = {}

    def update(self, competition, phase):
        if not isinstance(competition, str) or not competition:
            raise ValueError('Competition is required')
        if phase not in VALID_PHASES:
            raise ValueError('Invalid season phase')
        with self._lock:
            self._phases[competition] = phase

    def phase(self, competition):
        with self._lock:
            return self._phases.get(competition, UNKNOWN)

    def failed(self, competition):
        """A failed provider request must not overwrite confirmed season state."""
        return self.phase(competition)

    def eligible(self, competition, *, postseason_supported=False):
        phase = self.phase(competition)
        return phase == 'regular' or (phase == 'postseason' and postseason_supported)
