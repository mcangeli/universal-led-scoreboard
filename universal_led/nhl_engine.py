"""NHL game-to-frame adapter, independent of the MLB rendering pipeline."""
from __future__ import annotations

import time
from .nhl_runtime import select_games
from .nhl_visual import NHLVisualScreen
from .config_store import read_nhl_colors


class ConfiguredNHLRenderer:
    """Read cached feed snapshots; never perform network I/O during render."""

    def __init__(self, feed, *, favorite_teams=None, mode="fallback",
                 rotation_seconds=12, clock=time.monotonic, config_dir=None):
        self.feed = feed
        self.config_dir = config_dir
        self.clock = clock
        self.started = clock()
        self.timezone_name = "America/New_York"
        self.time_format = "12h"
        self.configure(favorite_teams=favorite_teams, mode=mode,
                       rotation_seconds=rotation_seconds)

    def configure(self, *, favorite_teams=None, mode="fallback",
                  rotation_seconds=12):
        if mode not in ("favorite", "fallback", "all"):
            raise ValueError("Invalid NHL rotation mode")
        if not isinstance(rotation_seconds, (int, float)) or isinstance(rotation_seconds, bool) or not 1 <= rotation_seconds <= 3600:
            raise ValueError("Invalid NHL rotation duration")
        teams = [] if favorite_teams is None else list(favorite_teams)
        if any(not isinstance(team, str) or len(team) != 3 or not team.isalpha() for team in teams):
            raise ValueError("Invalid NHL favorite team")
        self.favorite_teams = [team.upper() for team in teams]
        self.mode = mode
        self.rotation_seconds = rotation_seconds
        self.started = self.clock()

    def has_games(self):
        return bool(select_games(self.feed.games(), self.favorite_teams, self.mode))

    def has_live_games(self):
        """Check every eligible cached game, not just the currently selected one."""
        return any(game.status == "live" for game in
                   select_games(self.feed.games(), self.favorite_teams, self.mode))

    def game(self):
        games = select_games(self.feed.games(), self.favorite_teams, self.mode)
        if not games:
            return None
        live = [game for game in games if game.status == "live"]
        if live:
            games = live
        slot = int(max(0, self.clock() - self.started) // self.rotation_seconds)
        return games[slot % len(games)]

    def frame(self):
        game = self.game()
        # Read saved colors at render time so dashboard edits take effect without
        # restarting the web service. Failed reads retain the built-in defaults.
        colors = read_nhl_colors(self.config_dir) if self.config_dir is not None else None
        return NHLVisualScreen(game, timezone_name=self.timezone_name,
                               time_format=self.time_format, team_colors=colors).render()
