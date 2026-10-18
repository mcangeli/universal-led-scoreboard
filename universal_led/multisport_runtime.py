"""Shared MLB/NHL/NBA frame rotation, preserving the MLB supplemental rotation."""
from __future__ import annotations

import threading
import time
from .news_screen import NewsHeadlineScreen
from .display import Framebuffer


class MultiSportRenderer:
    """Route cached frames without network access; retain legacy single-sport mode."""

    def __init__(self, mlb_renderer, nhl_renderer, active_sport="mlb", clock=time.monotonic, news=None, settings_getter=None, nba_renderer=None, wnba_renderer=None, nfl_renderer=None, mls_renderer=None, nwsl_renderer=None, english_renderer=None, scoring_alerts=None, alert_renderer=None):
        self.mlb = mlb_renderer
        self.nhl = nhl_renderer
        self.nba = nba_renderer
        self.wnba = wnba_renderer
        self.nfl = nfl_renderer
        self.mls = mls_renderer
        self.nwsl = nwsl_renderer
        self.english = english_renderer
        self.scoring_alerts = scoring_alerts
        self.alert_renderer = alert_renderer
        self.clock = clock
        self.news = news
        self.settings_getter = settings_getter
        self._news_started = clock()
        self._lock = threading.Lock()
        self._active = "mlb"
        self._enabled = ("mlb",)
        self._interval = 12
        self._auto_rotation = False
        self._started = clock()
        self.set_active_sport(active_sport)

    @property
    def active_sport(self):
        with self._lock:
            return self._active

    def set_active_sport(self, sport):
        if sport not in self._supported():
            raise ValueError("Unsupported active sport")
        with self._lock:
            self._active = sport
            self._enabled = (sport,)
            self._auto_rotation = False
            self._started = self.clock()

    def _supported(self):
        return ("mlb", "nhl") + (("nba",) if self.nba is not None else ()) + (("wnba",) if self.wnba is not None else ()) + (("nfl",) if self.nfl is not None else ()) + (("mls",) if self.mls is not None else ()) + (("nwsl",) if self.nwsl is not None else ()) + (("english",) if self.english is not None else ())

    def configure_rotation(self, enabled_sports, interval=12, preferred="mlb"):
        supported = self._supported()
        enabled = tuple(s for s in supported if s in enabled_sports)
        if not enabled or preferred not in supported:
            raise ValueError("Invalid sport rotation")
        if type(interval) not in (int, float) or not 1 <= interval <= 3600:
            raise ValueError("Invalid sport rotation interval")
        with self._lock:
            self._enabled = enabled
            self._auto_rotation = len(enabled) > 1
            self._active = preferred if preferred in enabled else enabled[0]
            self._interval = interval
            self._started = self.clock()

    def _renderer(self, sport):
        return {"mlb": self.mlb, "nhl": self.nhl, "nba": self.nba,
                "wnba": self.wnba, "nfl": self.nfl, "mls": self.mls, "nwsl": self.nwsl, "english": self.english}.get(sport)

    def _available(self):
        """Skip score pages with no games; cached feeds decide today's games."""
        with self._lock:
            enabled = self._enabled
        available = []
        for sport in enabled:
            renderer = self._renderer(sport)
            if renderer is None:
                continue
            # Only renderers with an explicit availability contract can be
            # skipped. Legacy renderers and test doubles remain eligible.
            checker = getattr(renderer, "has_games", None)
            if not callable(checker):
                available.append(sport)
                continue
            try:
                if checker():
                    available.append(sport)
            except Exception:
                # Feed errors must not remove a sport from rotation.
                available.append(sport)
        return tuple(available)

    def _live_sports(self):
        """Return enabled sports with a currently live cached game.

        A renderer may expose has_live_games() for multi-game feeds. Otherwise
        game().status is used. Unknown or failed feed checks are not treated
        as proof of a live game.
        """
        with self._lock:
            enabled = self._enabled
        live = []
        for sport in enabled:
            renderer = self._renderer(sport)
            if renderer is None:
                continue
            checker = getattr(renderer, "has_live_games", None)
            try:
                if callable(checker):
                    active = bool(checker())
                else:
                    getter = getattr(renderer, "game", None)
                    game = getter() if callable(getter) else None
                    active = getattr(game, "status", None) == "live"
                if active:
                    live.append(sport)
            except Exception:
                continue
        return tuple(live)

    def _selected(self):
        with self._lock:
            if not self._auto_rotation:
                return self._active
        live = self._live_sports()
        available = live or self._available()
        if not available:
            return None
        with self._lock:
            interval = self._interval
            started = self._started
        slot = int(max(0, self.clock() - started) // interval)
        return available[slot % len(available)]

    def frame(self):
        # Optional scoring interruptions precede game/news rotation. A missing
        # adapter or disabled alerts leave the existing behavior unchanged.
        if self.scoring_alerts is not None and self.alert_renderer is not None:
            event = self.scoring_alerts.next_alert(self.clock())
            if event is not None:
                return self.alert_renderer(event)
        sport = self._selected()
        renderer = self._renderer(sport)
        if self.news is not None and self.settings_getter is not None:
            headlines = self.news.items()
            if headlines and self._live_sports():
                headlines = []
            game = renderer.game() if headlines and renderer is not None else None
            if headlines and (game is None or game.status != "live"):
                grouped = {}
                for item in headlines:
                    grouped.setdefault(item.source, []).append(item)
                sources = list(grouped)
                ordered = []
                for i in range(max(map(len, grouped.values()))):
                    for source in sources:
                        if i < len(grouped[source]):
                            ordered.append(grouped[source][i])
                timing = self.settings_getter()["news"]
                elapsed = max(0.0, self.clock() - self._news_started)
                interval = self._interval
                frequency = timing["rotation_interval"]
                if int(elapsed // interval) % frequency == frequency - 1:
                    page = int(elapsed // (frequency * interval)) % len(ordered)
                    item = ordered[page]
                    offset = int((elapsed % interval) * timing["scroll_chars_per_second"])
                    return NewsHeadlineScreen(item.text, item.source, offset=offset).render()
        return renderer.frame() if renderer is not None else Framebuffer(64, 32)

    def game(self):
        sport = self._selected()
        renderer = self._renderer(sport)
        return renderer.game() if renderer is not None else None
