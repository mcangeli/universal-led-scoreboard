"""Official NHL score feed with bounded I/O and last-good-data caching."""
from __future__ import annotations

import json
import threading
import time
from datetime import date
from urllib.request import urlopen

from .nhl_data import HockeyGame, parse_scoreboard

API_BASE = "https://api-web.nhle.com/v1/score"


def fetch_scores(day: date, *, timeout: float = 5.0) -> dict:
    """Fetch a single date. Caller controls polling and caching."""
    if not isinstance(day, date):
        raise TypeError("day must be a date")
    if not 0 < timeout <= 30:
        raise ValueError("timeout must be between 0 and 30 seconds")
    with urlopen(f"{API_BASE}/{day.isoformat()}", timeout=timeout) as response:
        return json.load(response)


class NHLFeed:
    """Thread-safe cached snapshots; failed refreshes preserve last good games.

    Fetch and clock are injectable so unit tests never contact the internet.
    """

    def __init__(self, *, fetcher=fetch_scores, refresh_seconds: float = 60,
                 clock=time.monotonic):
        if not 5 <= refresh_seconds <= 3600:
            raise ValueError("refresh_seconds must be between 5 and 3600")
        self.fetcher = fetcher
        self.refresh_seconds = refresh_seconds
        self.clock = clock
        self._lock = threading.Lock()
        self._refresh_lock = threading.Lock()
        self._day: date | None = None
        self._games: tuple[HockeyGame, ...] = ()
        self.last_error: str | None = None
        self.last_attempt: float | None = None
        self.last_success: float | None = None

    def refresh(self, day: date, *, force: bool = False) -> list[HockeyGame]:
        if not isinstance(day, date):
            raise TypeError("day must be a date")
        with self._refresh_lock:
            now = self.clock()
            with self._lock:
                if (not force and self._day == day and self.last_attempt is not None
                        and now - self.last_attempt < self.refresh_seconds):
                    return list(self._games)
                self.last_attempt = now
            try:
                parsed = tuple(parse_scoreboard(self.fetcher(day)))
            except Exception as exc:
                with self._lock:
                    self.last_error = str(exc)
                    return list(self._games)
            with self._lock:
                self._games = parsed
                self._day = day
                self.last_error = None
                self.last_success = self.clock()
                return list(self._games)

    def games(self) -> list[HockeyGame]:
        with self._lock:
            return list(self._games)

    def status(self) -> dict:
        with self._lock:
            return {
                "state": ("starting" if self.last_attempt is None else
                          "error" if self.last_error else "running"),
                "error": self.last_error,
                "games": len(self._games),
                "date": self._day.isoformat() if self._day else None,
                "last_attempt": self.last_attempt,
                "last_success": self.last_success,
            }
