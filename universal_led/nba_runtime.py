"""NBA background polling and favorite-team selection."""
import threading
from datetime import datetime
from zoneinfo import ZoneInfo

def select_games(games, teams=None, mode="fallback"):
    if mode not in ("favorite", "fallback", "all"):
        raise ValueError("Invalid NBA selection mode")
    if mode == "all" or not teams:
        return list(games)
    favorites = {str(team).upper() for team in ([teams] if isinstance(teams, str) else teams)}
    matched = [game for game in games if game.away in favorites or game.home in favorites]
    if mode == "favorite":
        return matched
    live = [game for game in games if game.status == "live"]
    if live:
        favorite_live = [game for game in live if game.away in favorites or game.home in favorites]
        return favorite_live or live
    return matched or list(games)

class BackgroundNBAFeed:
    def __init__(self, feed, day_provider=None, timezone_name="America/New_York", on_games=None):
        ZoneInfo(timezone_name)
        self.feed = feed
        self.on_games = on_games
        self.timezone_name = timezone_name
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
