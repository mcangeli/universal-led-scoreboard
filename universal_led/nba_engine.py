"""NBA cached-feed to 64x32 frame adapter."""
import time
from .nba_runtime import select_games
from .nba_screen import NBAScreen


class ConfiguredNBARenderer:
    def __init__(self, feed, *, favorite_teams=None, mode="fallback",
                 rotation_seconds=12, clock=time.monotonic):
        self.feed = feed
        self.clock = clock
        self.timezone_name = "America/New_York"
        self.time_format = "12h"
        self.configure(favorite_teams=favorite_teams, mode=mode,
                       rotation_seconds=rotation_seconds)

    def configure(self, *, favorite_teams=None, mode="fallback", rotation_seconds=12):
        if mode not in ("favorite", "fallback", "all"):
            raise ValueError("Invalid NBA rotation mode")
        if type(rotation_seconds) not in (int, float) or not 1 <= rotation_seconds <= 3600:
            raise ValueError("Invalid NBA rotation duration")
        teams = list(favorite_teams or [])
        if any(not isinstance(t, str) or len(t) != 3 or not t.isalpha() for t in teams):
            raise ValueError("Invalid NBA favorite team")
        self.favorite_teams = [t.upper() for t in teams]
        self.mode = mode
        self.rotation_seconds = rotation_seconds
        self.started = self.clock()

    def game(self):
        games = select_games(self.feed.games(), self.favorite_teams, self.mode)
        if not games:
            return None
        live = [g for g in games if g.status == "live"]
        if live:
            games = live
        return games[int(max(0, self.clock() - self.started) // self.rotation_seconds) % len(games)]

    def frame(self):
        return NBAScreen(self.game(), timezone_name=self.timezone_name,
                         time_format=self.time_format).render()
