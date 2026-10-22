"""NHL background worker and team selection."""
import threading
from datetime import datetime, timezone
from zoneinfo import ZoneInfo


def select_games(games, team=None, mode="fallback"):
    if mode not in ("favorite", "fallback", "all"):
        raise ValueError("Invalid selection mode")
    if mode == "all" or not team:
        return list(games)
    favorites = {s.upper() for s in ([team] if isinstance(team, str) else team)}
    matches = [g for g in games if g.away in favorites or g.home in favorites]
    if mode == "favorite":
        return matches
    live = [g for g in games if g.status == "live"]
    if live:
        favorite_live = [g for g in live if g.away in favorites or g.home in favorites]
        return favorite_live or live
    return matches or list(games)


class BackgroundNHLFeed:
    def __init__(self, feed, day_provider=None, timezone_name="America/New_York", on_games=None):
        self.feed = feed
        self.on_games = on_games
        self.timezone_name = timezone_name
        ZoneInfo(timezone_name)
        self.day_provider = day_provider or self._local_day
        self._stop = threading.Event()
        self._thread = None

    def _local_day(self):
        return datetime.now(ZoneInfo(self.timezone_name)).date()

    def set_timezone(self, timezone_name):
        ZoneInfo(timezone_name)
        self.timezone_name = timezone_name

    def refresh_once(self):
        games = self.feed.refresh(self.day_provider())
        if self.on_games is not None and self.feed.status().get("state") != "error":
            self.on_games(games)
        return games

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
