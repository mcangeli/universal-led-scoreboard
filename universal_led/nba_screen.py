"""Compact basketball-specific 64x32 score presentation."""
from dataclasses import dataclass
from zoneinfo import ZoneInfo

from .display import Framebuffer
from .mlb_classic import small
from .nba_data import BasketballGame

WHITE = (235, 235, 225)
ORANGE = (245, 155, 55)
DIM = (100, 112, 128)
RED = (245, 90, 75)
TEAM = (135, 200, 245)


def status_text(game: BasketballGame, timezone_name="America/New_York", time_format="12h"):
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
        return "FINAL" + (" " + ("OT" if game.period == 5 else str(game.period - 4) + "OT")
                          if game.period and game.period > 4 else "")
    if game.status == "live":
        detail = game.detail.upper()
        if "HALF" in detail:
            return "HALFTIME"
        if "END" in detail and "PERIOD" in detail:
            return "END Q" + str(game.period or "")
        period = ("Q" + str(game.period)) if game.period and game.period <= 4 else (
            (str(game.period - 4) + "OT") if game.period and game.period > 5 else "OT")
        return period + (" " + game.clock if game.clock and game.clock != "0:00" else "")
    return "NBA"


@dataclass(frozen=True)
class NBAScreen:
    game: BasketballGame | None = None
    name: str = "nba-classic"
    timezone_name: str = "America/New_York"
    time_format: str = "12h"
    league: str = "NBA"

    def render(self) -> Framebuffer:
        fb = Framebuffer(64, 32)
        if self.league not in ("NBA", "WNBA"):
            raise ValueError("Unsupported basketball league")
        small(fb, self.league, 1, 1, ORANGE)
        # Basketball motif: an original tiny four-pixel ball/cross.
        for x, y in ((55, 2), (56, 1), (56, 3), (57, 2)):
            fb.pixel(x, y, ORANGE)
        for x in range(1, 63):
            fb.pixel(x, 7, DIM)
            fb.pixel(x, 25, DIM)
        if self.game is None:
            small(fb, "NO GAMES", 12, 15, WHITE)
            return fb
        for y, team, score in ((10, self.game.away, self.game.away_score),
                               (18, self.game.home, self.game.home_score)):
            small(fb, team[:3].ljust(3), 2, y, TEAM if y == 18 else WHITE)
            # Three digits occupy 12 pixels; never truncate a normal NBA score.
            digits = "-" if score is None else str(score)
            if len(digits) > 4:
                digits = "9999+"
            small(fb, digits, max(24, 62 - 4 * len(digits)), y, ORANGE)
        label = status_text(self.game, self.timezone_name, self.time_format)[:15]
        small(fb, label, 2, 27, RED if self.game.status == "postponed" else ORANGE)
        return fb
