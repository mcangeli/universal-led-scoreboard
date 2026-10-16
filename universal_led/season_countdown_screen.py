"""Compact, readable 64x32 season countdown renderer."""
from dataclasses import dataclass
from .display import Framebuffer
from .mlb_classic import small
from .safe_layout import fit_small, small_center_x
from .season_countdown import Countdown

GOLD = (239, 195, 95)
WHITE = (240, 240, 235)
DIM = (115, 155, 185)

@dataclass(frozen=True)
class SeasonCountdownScreen:
    result: Countdown

    def render(self):
        fb = Framebuffer(64, 32)
        event = self.result.milestone
        heading = fit_small(event.sport.upper() + ' OPENING', 62)
        small(fb, heading, small_center_x(heading), 2, GOLD)
        for x in range(2, 62):
            fb.pixel(x, 9, (50, 70, 88))

        days = str(self.result.days)
        if len(days) <= 3:
            # Large numerals anchor the layout; the unit remains secondary.
            number_width = len(days) * 6 - 1
            group_width = number_width + 3 + 4 * 4 - 1
            x = (64 - group_width) // 2
            fb.text(days, x, 13, WHITE)
            small(fb, 'DAYS', x + number_width + 3, 15, GOLD)
        else:
            # Graceful fallback for unusually distant season milestones.
            label = fit_small(days + ' DAYS', 62)
            small(fb, label, small_center_x(label), 15, WHITE)

        sub = f'{self.result.hours:02d}H {self.result.minutes:02d}M'
        small(fb, sub, small_center_x(sub), 25, DIM)
        return fb
