"""NBA score polling with bounded transport and last-good snapshot caching."""
import json
import threading
import time
from datetime import date
from urllib.request import Request, urlopen
from .nba_data import parse_scoreboard

API_BASE = "https://site.api.espn.com/apis/site/v2/sports/basketball/nba/scoreboard"

def fetch_scores(day: date, *, timeout=5.0):
    if not isinstance(day, date):
        raise TypeError("day must be a date")
    if not isinstance(timeout, (int, float)) or isinstance(timeout, bool) or not 0 < timeout <= 30:
        raise ValueError("Invalid timeout")
    request = Request(f"{API_BASE}?dates={day:%Y%m%d}", headers={
        "User-Agent": "UniversalLEDScoreboard/0.3",
        "Accept": "application/json"})
    with urlopen(request, timeout=timeout) as response:
        return json.load(response)

class NBAFeed:
    def __init__(self, *, fetcher=fetch_scores, refresh_seconds=60, clock=time.monotonic):
        if type(refresh_seconds) not in (int, float) or not 5 <= refresh_seconds <= 3600:
            raise ValueError("Invalid NBA refresh interval")
        self.fetcher = fetcher
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
                if not force and self._day == day and self.last_attempt is not None and now - self.last_attempt < self.refresh_seconds:
                    return list(self._games)
                self.last_attempt = now
            try:
                games = tuple(parse_scoreboard(self.fetcher(day)))
            except Exception as exc:
                with self._lock:
                    self.last_error = str(exc)
                    return list(self._games)
            with self._lock:
                self._games = games
                self._day = day
                self.last_success = self.clock()
                self.last_error = None
                return list(self._games)

    def games(self):
        with self._lock:
            return list(self._games)

    def status(self):
        with self._lock:
            return {"state": "starting" if self.last_attempt is None else "error" if self.last_error else "running",
                "error": self.last_error, "games": len(self._games),
                "date": self._day.isoformat() if self._day else None,
                "last_attempt": self.last_attempt, "last_success": self.last_success}
