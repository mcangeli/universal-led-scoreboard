"""NHL background worker and team selection."""
import threading
from datetime import datetime, timezone


def select_games(games, team=None, mode="fallback"):
    if mode not in ("favorite", "fallback", "all"):
        raise ValueError("Invalid selection mode")
    if mode == "all" or not team:
        return list(games)
    favorites = {s.upper() for s in ([team] if isinstance(team, str) else team)}
    matches = [g for g in games if g.away in favorites or g.home in favorites]
    return matches if matches or mode == "favorite" else list(games)


class BackgroundNHLFeed:
    def __init__(self, feed, day_provider=None):
        self.feed = feed
        self.day_provider = day_provider or (lambda: datetime.now(timezone.utc).date())
        self._stop = threading.Event()
        self._thread = None

    def refresh_once(self):
        return self.feed.refresh(self.day_provider())

    def _run(self):
        while not self._stop.is_set():
            self.refresh_once()
            self._stop.wait(self.feed.refresh_seconds)

    def start(self):
        if self._thread is None:
            self._stop.clear()
            self._thread = threading.Thread(target=self._run, daemon=True)
            self._thread.start()

    def stop(self):
        self._stop.set()
        if self._thread is not None:
            self._thread.join(timeout=10)
            if not self._thread.is_alive():
                self._thread = None

    def games(self):
        return self.feed.games()

    def status(self):
        return self.feed.status()
