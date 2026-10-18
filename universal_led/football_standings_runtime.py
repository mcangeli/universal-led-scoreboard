"""Thread-safe, cached standings refresh with no network work during rendering."""
import threading
import time

from .football_standings_feed import fetch_football_standings


class FootballStandingsCache:
    def __init__(self, league, *, fetcher=fetch_football_standings,
                 refresh_seconds=900, clock=time.monotonic):
        if type(refresh_seconds) not in (int, float) or not 60 <= refresh_seconds <= 86400:
            raise ValueError("Invalid standings refresh interval")
        self.league = league
        self.fetcher = fetcher
        self.refresh_seconds = refresh_seconds
        self.clock = clock
        self._lock = threading.Lock()
        self._refresh_lock = threading.Lock()
        self._rows = ()
        self.last_attempt = None
        self.last_success = None
        self.last_error = None

    def refresh(self, *, force=False):
        with self._refresh_lock:
            now = self.clock()
            with self._lock:
                if (not force and self.last_attempt is not None
                        and now - self.last_attempt < self.refresh_seconds):
                    return self._rows
                self.last_attempt = now
            try:
                rows = tuple(self.fetcher(self.league))
            except Exception as exc:
                with self._lock:
                    self.last_error = str(exc)
                    return self._rows
            with self._lock:
                self._rows = rows
                self.last_success = self.clock()
                self.last_error = None
                return self._rows

    def rows(self):
        with self._lock:
            return self._rows

    def status(self):
        with self._lock:
            return {
                "league": self.league,
                "state": "starting" if self.last_attempt is None else
                         "error" if self.last_error else "running",
                "error": self.last_error,
                "teams": len(self._rows),
                "last_attempt": self.last_attempt,
                "last_success": self.last_success,
            }


class BackgroundFootballStandings:
    def __init__(self, cache):
        self.cache = cache
        self._stop = threading.Event()
        self._thread = None

    def start(self):
        if self._thread is not None and self._thread.is_alive():
            return
        self._stop.clear()
        self._thread = threading.Thread(target=self._run, daemon=True,
                                        name="standings-" + self.cache.league)
        self._thread.start()

    def _run(self):
        while not self._stop.is_set():
            self.cache.refresh()
            self._stop.wait(self.cache.refresh_seconds)

    def stop(self):
        self._stop.set()
        if self._thread is not None:
            self._thread.join(timeout=3)
            self._thread = None
