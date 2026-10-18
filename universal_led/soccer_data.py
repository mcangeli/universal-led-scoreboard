"""Cached ESPN soccer scoreboard polling for MLS and NWSL.

Network requests happen only during refresh, never during frame rendering.
"""
import json
import threading
import time
from datetime import date
from urllib.request import Request, urlopen

from .soccer_feed import parse_scoreboard

LEAGUE_SLUGS = {"MLS": "usa.1", "NWSL": "usa.nwsl",
                "EPL": "eng.1", "CHAMPIONSHIP": "eng.2",
                "LEAGUE_ONE": "eng.3", "LEAGUE_TWO": "eng.4"}
API_BASE = "https://site.api.espn.com/apis/site/v2/sports/soccer"


def fetch_scores(league: str, day: date, *, timeout=5.0):
    if league not in LEAGUE_SLUGS:
        raise ValueError("Unsupported soccer league")
    if not isinstance(day, date):
        raise TypeError("day must be a date")
    if type(timeout) not in (int, float) or not 0 < timeout <= 30:
        raise ValueError("Invalid timeout")
    url = f"{API_BASE}/{LEAGUE_SLUGS[league]}/scoreboard?dates={day:%Y%m%d}"
    request = Request(url, headers={
        "User-Agent": "UniversalLEDScoreboard/0.5",
        "Accept": "application/json",
    })
    with urlopen(request, timeout=timeout) as response:
        return json.load(response)


class SoccerFeed:
    def __init__(self, league: str, *, fetcher=fetch_scores, refresh_seconds=60,
                 clock=time.monotonic, provider=None, enrich=None):
        if league not in LEAGUE_SLUGS:
            raise ValueError("Unsupported soccer league")
        if type(refresh_seconds) not in (int, float) or not 5 <= refresh_seconds <= 3600:
            raise ValueError("Invalid soccer refresh interval")
        self.league = league
        self.fetcher = fetcher
        self.provider = provider
        self.enrich = enrich
        self.refresh_seconds = refresh_seconds
        self.clock = clock
        self._lock = threading.Lock()
        self._refresh_lock = threading.Lock()
        self._day = None
        self._games = ()
        self.last_attempt = None
        self.last_success = None
        self.last_error = None

    def refresh(self, day: date, *, force=False):
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
                games = (tuple(self.provider.fetch(day)) if self.provider is not None else
                         tuple(parse_scoreboard(self.fetcher(self.league, day), self.league)))
            except Exception as exc:
                with self._lock:
                    self.last_error = str(exc)
                    return list(self._games)
            if self.enrich is not None:
                # Enrichment failures must never hide otherwise valid scores.
                try:
                    games = tuple(self.enrich(game) for game in games)
                except Exception:
                    pass
            with self._lock:
                self._games = games
                self._day = day
                self.last_success = self.clock()
                self.last_error = None
                return list(games)

    def games(self):
        with self._lock:
            return list(self._games)

    def status(self):
        with self._lock:
            return {
                "state": "starting" if self.last_attempt is None else
                         "error" if self.last_error else "running",
                "error": self.last_error,
                "games": len(self._games),
                "date": self._day.isoformat() if self._day else None,
                "last_attempt": self.last_attempt,
                "last_success": self.last_success,
            }
