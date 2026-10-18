"""Coordinated rotation of enabled English football divisions.

Consumes already-refreshed feeds; never polls a network during frame rendering.
"""
import time

from .english_football import COMPETITIONS
from .soccer_display import SoccerDisplayController
from .soccer_scoring_alerts import observe_soccer_match
from .soccer_pixels import render_soccer_screen
from .soccer_rotation import eligible_matches, prioritize_live, is_live


class EnglishFootballRenderer:
    def __init__(self, feeds, *, enabled=None, favorite_teams=(), mode="fallback",
                 rotation_seconds=12, goal_seconds=8, clock=time.monotonic, scoring_alerts=None):
        if not isinstance(feeds, dict) or any(key not in COMPETITIONS for key in feeds):
            raise ValueError("Expected English competition feed mapping")
        self.feeds = dict(feeds)
        self.clock = clock
        self.scoring_alerts = scoring_alerts
        self.display = SoccerDisplayController(goal_seconds)
        self.configure(enabled=enabled, favorite_teams=favorite_teams,
                       mode=mode, rotation_seconds=rotation_seconds)

    def configure(self, *, enabled=None, favorite_teams=(), mode="fallback", rotation_seconds=12):
        if mode not in ("favorite", "fallback", "all"):
            raise ValueError("Invalid English football rotation mode")
        if type(rotation_seconds) not in (int, float) or not 1 <= rotation_seconds <= 3600:
            raise ValueError("Invalid rotation interval")
        selected = set(self.feeds) if enabled is None else set(enabled)
        if not selected <= COMPETITIONS.keys():
            raise ValueError("Unknown English competition")
        self.enabled = frozenset(selected)
        self.favorite_teams = tuple(str(team).strip().upper() for team in favorite_teams)
        self.mode = mode
        self.rotation_seconds = rotation_seconds
        self.started = self.clock()

    def _games(self):
        matches = []
        for league in COMPETITIONS:
            if league not in self.enabled or league not in self.feeds:
                continue
            matches.extend(match for match in self.feeds[league].games() if match.league == league)
        # Live games outrank scheduled favorite fixtures. Apply favorites
        # within the live pool, not across matches in different states.
        matches = prioritize_live(matches)
        return eligible_matches(matches, favorites=self.favorite_teams,
                                mode="favorites" if self.mode == "favorite" else self.mode)

    def has_games(self):
        return bool(self._games())

    def has_live_games(self):
        return any(is_live(match) for match in self._games())

    def game(self):
        matches = prioritize_live(self._games())
        if not matches:
            return None
        slot = int(max(0, self.clock() - self.started) // self.rotation_seconds)
        return matches[slot % len(matches)]

    def frame(self):
        from .display import Framebuffer
        match = self.game()
        if match is None:
            return Framebuffer(64, 32)
        return render_soccer_screen(self.display.screen(match, self.clock()))

    def update(self, match):
        if match.league in self.enabled and match.league in self.feeds:
            self.display.update(match, announce=not (self.scoring_alerts is not None
                                                    and self.scoring_alerts.enabled))
            if self.scoring_alerts is not None:
                observe_soccer_match(self.scoring_alerts, match,
                                     favorite_teams=self.favorite_teams)
