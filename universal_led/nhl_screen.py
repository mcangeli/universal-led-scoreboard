"""Compact NHL scoreboard on the shared 64x32 RGB framebuffer."""
from __future__ import annotations

from dataclasses import dataclass
from zoneinfo import ZoneInfo

from .display import Framebuffer
from .mlb_classic import small
from .nhl_data import HockeyGame

WHITE = (235, 235, 225)
GOLD = (239, 195, 95)
DIM = (110, 125, 140)
ICE = (105, 185, 235)
RED = (240, 80, 70)


def status_text(game: HockeyGame, timezone_name: str = 'America/New_York', time_format: str = '12h') -> str:
    if game.status == "postponed":
        return "PPD"
    if game.status == "scheduled":
        if game.start_utc is None:
            return "PREGAME"
        local = game.start_utc.astimezone(ZoneInfo(timezone_name))
        if time_format == '24h':
            return local.strftime('%H:%M %Z')
        return local.strftime('%I:%M%p').lstrip('0') + ' ' + local.tzname()
    if game.status == "final":
        if game.shootout:
            return "FINAL SO"
        if game.period_label == "OT":
            return "FINAL OT"
        return "FINAL"
    if game.status == "live":
        if game.intermission:
            return "INT"
        if game.shootout or game.period_label == "SO":
            return "SO"
        period = "OT" if game.period_label == "OT" else (
            "P" + str(game.period) if game.period is not None else "LIVE")
        return period + (" " + game.clock if game.clock else "")
    return "NHL"


@dataclass(frozen=True)
class NHLScreen:
    game: HockeyGame | None = None
    name: str = "nhl-classic"
    timezone_name: str = "America/New_York"
    time_format: str = "12h"

    def render(self) -> Framebuffer:
        fb = Framebuffer(64, 32)
        # Header and separator make the layout recognizably hockey-specific.
        small(fb, "NHL", 1, 1, ICE)
        for x in range(1, 63):
            fb.pixel(x, 7, DIM)
        if self.game is None:
            small(fb, "NO GAMES", 12, 14, WHITE)
            return fb
        g = self.game
        # Abbreviations and scores have fixed, non-overlapping columns.
        small(fb, g.away[:3].ljust(3), 2, 10, WHITE)
        small(fb, g.home[:3].ljust(3), 2, 18, ICE)
        for y, score in ((10, g.away_score), (18, g.home_score)):
            text = "-" if score is None else str(min(score, 99))
            small(fb, text, 53 - 4 * len(text), y, GOLD)
        for x in range(1, 63):
            fb.pixel(x, 25, DIM)
        # Bottom status is truncated to the available 15 glyph cells.
        label = status_text(g, self.timezone_name, self.time_format)[:15]
        small(fb, label, 2, 27, RED if g.status == "postponed" else GOLD)
        return fb
