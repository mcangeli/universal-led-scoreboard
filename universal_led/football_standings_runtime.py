"""Thread-safe, cached standings refresh with no network work during rendering."""
import threading
import time
import json
import os
from dataclasses import asdict
from pathlib import Path

from .standings import Standing

from .football_standings_feed import fetch_football_standings


class FootballStandingsCache:
    def __init__(self, league, *, fetcher=fetch_football_standings,
                 refresh_seconds=900, clock=time.monotonic, cache_dir=None,
                 cache_key=None, expected_group=None):
        if type(refresh_seconds) not in (int, float) or not 60 <= refresh_seconds <= 86400:
            raise ValueError("Invalid standings refresh interval")
        self.league = league
        self.cache_key = cache_key or league
        self.expected_group = expected_group
        self.cache_path = (Path(cache_dir) / (self.cache_key.lower() + ".json")) if cache_dir is not None else None
        self.fetcher = fetcher
        self.refresh_seconds = refresh_seconds
        self.clock = clock
        self._lock = threading.Lock()
        self._refresh_lock = threading.Lock()
        self._rows = ()
        self.last_attempt = None
        self.last_success = None
        self.last_error = None
        self._load_disk()

    def _load_disk(self):
        if self.cache_path is None:
            return
        try:
            payload = json.loads(self.cache_path.read_text(encoding="utf-8"))
            if payload.get("league") != self.league or payload.get("cache_key", self.league) != self.cache_key:
                return
            rows = tuple(Standing(**item) for item in payload["rows"])
            if rows and all(row.league == self.league and
                            (self.expected_group is None or row.group == self.expected_group)
                            for row in rows):
                self._rows = rows
        except (OSError, ValueError, TypeError, KeyError):
            return

    def _save_disk(self, rows):
        if self.cache_path is None or not rows:
            return
        try:
            self.cache_path.parent.mkdir(parents=True, exist_ok=True)
            temp = self.cache_path.with_suffix(".tmp")
            temp.write_text(json.dumps({"league": self.league, "cache_key": self.cache_key, "rows": [asdict(row) for row in rows]}),
                            encoding="utf-8")
            os.replace(temp, self.cache_path)
        except OSError:
            return

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
            if not rows:
                with self._lock:
                    self.last_error = "Standings feed returned no teams"
                    return self._rows
            # Preserve the generic in-memory cache contract used by existing
            # callers. Enforce record identity for persistent or group-bound feeds.
            if (self.cache_path is not None or self.expected_group is not None) and any(
                    not isinstance(row, Standing) or row.league != self.league or
                    (self.expected_group is not None and row.group != self.expected_group)
                    for row in rows):
                with self._lock:
                    self.last_error = "Standings feed returned a different league or group"
                    return self._rows
            if rows and all(isinstance(row, Standing) for row in rows):
                self._save_disk(rows)
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
