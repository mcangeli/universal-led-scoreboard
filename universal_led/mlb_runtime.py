"""Non-blocking MLB feed worker and game selection for Preview 7."""
from __future__ import annotations
import threading
import time
from .mlb_data import MLBFeed
from .mlb_classic import BaseballGame

def select_games(games: list[BaseballGame], team: str | None = 'ATL',
                 mode: str = 'fallback') -> list[BaseballGame]:
    """favorite: team only; fallback: team if playing else all; all: every game."""
    if mode not in ('favorite', 'fallback', 'all'):
        raise ValueError('mode must be favorite, fallback, or all')
    if mode == 'all' or not team:
        return list(games)
    matches = [g for g in games if team.upper() in (g.away, g.home)]
    return matches if matches or mode == 'favorite' else list(games)

class BackgroundMLBFeed:
    """Only the worker calls the network. Browser requests read cached snapshots."""
    def __init__(self, feed: MLBFeed):
        self.feed = feed
        self._stop = threading.Event()
        self._thread: threading.Thread | None = None
        self._lock = threading.Lock()
        self._games: list[BaseballGame] = []
        self.last_error: str | None = None
        self.last_attempt: float | None = None
        self.last_success: float | None = None

    def refresh_once(self):
        games = self.feed.games()
        now = time.time()
        with self._lock:
            self._games = games
            self.last_error = self.feed.last_error
            self.last_attempt = now
            if self.last_error is None:
                self.last_success = now

    def start(self):
        if self._thread is not None:
            return
        self._thread = threading.Thread(target=self._run, name='mlb-feed', daemon=True)
        self._thread.start()

    def _run(self):
        while not self._stop.is_set():
            try:
                self.refresh_once()
            except Exception as exc:
                with self._lock:
                    self.last_error = str(exc)
                    self.last_attempt = time.time()
            self._stop.wait(self.feed.refresh_seconds)

    def games(self):
        with self._lock:
            return list(self._games)

    def status(self):
        with self._lock:
            state = ('starting' if self.last_attempt is None else
                     'error' if self.last_error else 'running')
            return {'state':state,'error':self.last_error,'games':len(self._games),
                    'last_attempt':self.last_attempt,'last_success':self.last_success}

    def stop(self):
        self._stop.set()
        if self._thread is not None:
            self._thread.join(timeout=10)
