"""LED-friendly NHL presentation with team accents and compact puck marks.

Original symbolic pixel artwork, not official NHL logos.
"""
from __future__ import annotations

from dataclasses import dataclass
from .display import Framebuffer
from .mlb_classic import small
from .nhl_data import HockeyGame
from .nhl_screen import status_text, GOLD, DIM, WHITE, ICE, RED

TEAM_COLORS = {
    "ANA": (238, 113, 43), "BOS": (245, 195, 45),
    "BUF": (245, 186, 50), "CGY": (230, 53, 61),
    "CAR": (226, 52, 63), "CHI": (220, 52, 59),
    "COL": (150, 54, 83), "CBJ": (68, 110, 181),
    "DAL": (43, 170, 119), "DET": (228, 45, 61),
    "EDM": (235, 114, 40), "FLA": (221, 55, 65),
    "LAK": (190, 194, 202), "MIN": (68, 135, 96),
    "MTL": (217, 51, 69), "NSH": (244, 195, 56),
    "NJD": (223, 51, 61), "NYI": (245, 119, 42),
    "NYR": (67, 117, 213), "OTT": (205, 54, 65),
    "PHI": (240, 115, 43), "PIT": (241, 193, 57),
    "SEA": (91, 190, 194), "SJS": (43, 155, 168),
    "STL": (75, 126, 220), "TBL": (66, 121, 215),
    "TOR": (64, 123, 218), "UTA": (100, 164, 209),
    "VAN": (68, 133, 188), "VGK": (201, 168, 90),
    "WSH": (212, 52, 68), "WPG": (87, 151, 206),
}


def draw_puck(fb: Framebuffer, x: int, y: int, color=ICE):
    """Tiny original 7x5 puck silhouette."""
    for dy, row in enumerate(("0111110", "1111111", "1111111", "0111110", "0011100")):
        for dx, bit in enumerate(row):
            if bit == "1":
                fb.pixel(x + dx, y + dy, color)


@dataclass(frozen=True)
class NHLVisualScreen:
    game: HockeyGame | None = None
    name: str = "nhl-visual"
    timezone_name: str = "America/New_York"
    time_format: str = "12h"

    def render(self) -> Framebuffer:
        fb = Framebuffer(64, 32)
        small(fb, "NHL", 1, 1, ICE)
        draw_puck(fb, 53, 1)
        for x in range(1, 63):
            fb.pixel(x, 7, DIM)
            fb.pixel(x, 25, DIM)
        if self.game is None:
            small(fb, "NO GAMES", 12, 15, WHITE)
            return fb
        g = self.game
        for y, team, score in ((10, g.away, g.away_score),
                               (18, g.home, g.home_score)):
            accent = TEAM_COLORS.get(team, WHITE)
            small(fb, team[:3].ljust(3), 2, y, accent)
            # Team-colored mini puck keeps the sport's visual language.
            draw_puck(fb, 24, y, accent)
            digits = "-" if score is None else str(min(score, 99))
            small(fb, digits, 59 - 4 * len(digits), y, GOLD)
        label = status_text(g, self.timezone_name, self.time_format)[:15]
        small(fb, label, 2, 27, RED if g.status == "postponed" else GOLD)
        return fb
