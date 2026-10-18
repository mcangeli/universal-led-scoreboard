"""NFL cached-feed to 64x32 frame adapter."""
import time
from .nfl_runtime import select_games
from .game_interruptions import InterruptionPolicy, filter_interrupted_games
from .nfl_screen import NFLScreen

class ConfiguredNFLRenderer:
    def __init__(self, feed, *, favorite_teams=None, mode="fallback",
                 rotation_seconds=12, clock=time.monotonic):
        self.feed = feed
        self.interruption_policy = InterruptionPolicy()
        self.external_live_games = False
        self.clock = clock
        self.timezone_name = "America/New_York"
        self.time_format = "12h"
        self.configure(favorite_teams=favorite_teams, mode=mode,
                       rotation_seconds=rotation_seconds)

    def configure(self, *, favorite_teams=None, mode="fallback", rotation_seconds=12):
        if mode not in ("favorite", "fallback", "all"):
            raise ValueError("Invalid NFL rotation mode")
        if type(rotation_seconds) not in (int, float) or not 1 <= rotation_seconds <= 3600:
            raise ValueError("Invalid NFL rotation duration")
        teams = list(favorite_teams or [])
        if any(not isinstance(t, str) or not 2 <= len(t) <= 3 or not t.isalpha() for t in teams):
            raise ValueError("Invalid NFL favorite team")
        self.favorite_teams = [t.upper() for t in teams]
        self.mode = mode
        self.rotation_seconds = rotation_seconds
        self.started = self.clock()

    def _eligible_games(self):
        selected = select_games(self.feed.games(), self.favorite_teams, self.mode)
        return filter_interrupted_games(selected, has_live_games=self.external_live_games,
                                        policy=self.interruption_policy)

    def has_games(self):
        return bool(self._eligible_games())

    def has_live_games(self):
        """Check every eligible cached game, not just the currently selected one."""
        return any(game.status == "live" for game in
                   self._eligible_games())

    def game(self):
        games = self._eligible_games()
        if not games:
            return None
        live = [g for g in games if g.status == "live"]
        if live:
            games = live
        return games[int(max(0, self.clock() - self.started) // self.rotation_seconds) % len(games)]

    def frame(self):
        return NFLScreen(self.game(), timezone_name=self.timezone_name,
                         time_format=self.time_format).render()
