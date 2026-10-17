"""LED-friendly NHL presentation with team accents and compact puck marks.

Original symbolic pixel artwork, not official NHL logos.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Mapping
from .colors import readable_on_black
from .display import Framebuffer
from .mlb_classic import small
from .nhl_data import HockeyGame
from .nhl_colors import NHL_TEAM_COLORS
from .nhl_screen import status_text, GOLD, DIM, WHITE, ICE, RED

TEAM_COLORS = NHL_TEAM_COLORS


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
    team_colors: Mapping[str, tuple[int, int, int]] | None = None

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
        for y, team, score, record in ((10, g.away, g.away_score, g.away_record),
                                       (18, g.home, g.home_score, g.home_record)):
            accent = readable_on_black((self.team_colors or TEAM_COLORS).get(team, WHITE))
            small(fb, team[:3].ljust(3), 2, y, accent)
            # Team-colored mini puck keeps the sport's visual language.
            draw_puck(fb, 24, y, accent)
            digits = (record[:9] if record else "-") if g.status == "scheduled" else ("-" if score is None else str(min(score, 99)))
            small(fb, digits, max(24, 59 - 4 * len(digits)), y, GOLD)
        label = status_text(g, self.timezone_name, self.time_format)[:15]
        small(fb, label, 2, 27, RED if g.status == "postponed" else GOLD)
        return fb
