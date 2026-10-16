"""Compact 64x32 NFL Classic score display."""
from dataclasses import dataclass
from zoneinfo import ZoneInfo

from .display import Framebuffer
from .mlb_classic import small
from .nfl_data import FootballGame

WHITE = (235, 235, 225)
GOLD = (245, 175, 60)
DIM = (100, 112, 128)
RED = (245, 90, 75)
TEAM = (135, 200, 245)


def status_text(game: FootballGame, timezone_name="America/New_York", time_format="12h"):
    if game.status == "postponed":
        return "PPD"
    if game.status == "scheduled":
        if game.start_utc is None:
            return "PREGAME"
        local = game.start_utc.astimezone(ZoneInfo(timezone_name))
        if time_format == "24h":
            return local.strftime("%H:%M %Z")
        return local.strftime("%I:%M%p").lstrip("0") + " " + local.tzname()
    if game.status == "final":
        return "FINAL" + (" OT" if game.period and game.period > 4 else "")
    if game.status == "live":
        detail = game.detail.upper()
        if "HALF" in detail:
            return "HALFTIME"
        if "END" in detail and ("QUARTER" in detail or "PERIOD" in detail):
            return "END Q" + str(game.period or "")
        period = ("Q" + str(game.period)) if game.period and game.period <= 4 else "OT"
        return period + (" " + game.clock if game.clock and game.clock != "0:00" else "")
    return "NFL"


@dataclass(frozen=True)
class NFLScreen:
    game: FootballGame | None = None
    name: str = "nfl-classic"
    timezone_name: str = "America/New_York"
    time_format: str = "12h"

    def render(self) -> Framebuffer:
        fb = Framebuffer(64, 32)
        small(fb, "NFL", 1, 1, GOLD)
        # Original tiny football silhouette.
        for x, y in ((54, 2), (55, 1), (55, 2), (55, 3),
                     (56, 1), (56, 2), (56, 3), (57, 2)):
            fb.pixel(x, y, GOLD)
        for x in range(1, 63):
            fb.pixel(x, 7, DIM)
            fb.pixel(x, 25, DIM)
        if self.game is None:
            small(fb, "NO GAMES", 12, 15, WHITE)
            return fb
        pregame = self.game.status == "scheduled"
        for y, team, score, record in ((10, self.game.away, self.game.away_score, self.game.away_record),
                                       (18, self.game.home, self.game.home_score, self.game.home_record)):
            small(fb, team[:3].ljust(3), 2, y, TEAM if y == 18 else WHITE)
            digits = (record[:9] if record else "-") if pregame else ("-" if score is None else str(score))
            small(fb, digits, max(22, 62 - 4 * len(digits)), y, GOLD)
        small(fb, status_text(self.game, self.timezone_name, self.time_format)[:15],
              2, 27, RED if self.game.status == "postponed" else GOLD)
        return fb
