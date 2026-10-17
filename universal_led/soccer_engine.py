"""Cached soccer feed adapter for the existing MultiSportRenderer contract."""
import time

from .soccer_display import SoccerDisplayController
from .soccer_pixels import render_soccer_screen
from .soccer_rotation import eligible_matches, prioritize_live, is_live


class ConfiguredSoccerRenderer:
    def __init__(self, feed, *, league, favorite_teams=(), mode="fallback",
                 rotation_seconds=12, goal_seconds=8, clock=time.monotonic):
        if league not in ("MLS", "NWSL"):
            raise ValueError("Unsupported soccer league")
        self.feed = feed
        self.league = league
        self.clock = clock
        self.display = SoccerDisplayController(goal_seconds)
        self.configure(favorite_teams=favorite_teams, mode=mode, rotation_seconds=rotation_seconds)

    def configure(self, *, favorite_teams=(), mode="fallback", rotation_seconds=12):
        if mode not in ("favorite", "fallback", "all"):
            raise ValueError("Invalid soccer rotation mode")
        if type(rotation_seconds) not in (int, float) or not 1 <= rotation_seconds <= 3600:
            raise ValueError("Invalid soccer rotation interval")
        self.favorite_teams = tuple(str(team).strip().upper() for team in favorite_teams)
        self.mode = mode
        self.rotation_seconds = rotation_seconds
        self.started = self.clock()

    def _games(self):
        games = (game for game in self.feed.games() if game.league == self.league)
        mode = "favorites" if self.mode == "favorite" else self.mode
        return eligible_matches(games, favorites=self.favorite_teams, mode=mode)

    def has_games(self):
        return bool(self._games())

    def has_live_games(self):
        return any(is_live(game) for game in self._games())

    def game(self):
        games = prioritize_live(self._games())
        if not games:
            return None
        slot = int(max(0, self.clock() - self.started) // self.rotation_seconds)
        return games[slot % len(games)]

    def frame(self):
        from .display import Framebuffer
        game = self.game()
        if game is None:
            return Framebuffer(64, 32)
        return render_soccer_screen(self.display.screen(game, self.clock()))

    def update(self, match):
        if match.league == self.league:
            self.display.update(match)
