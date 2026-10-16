"""Shared 64x32 season countdown renderer."""
from dataclasses import dataclass
from .display import Framebuffer
from .mlb_classic import small
from .safe_layout import fit_small, small_center_x
from .season_countdown import Countdown

@dataclass(frozen=True)
class SeasonCountdownScreen:
    result: Countdown

    def render(self):
        fb = Framebuffer(64, 32)
        event = self.result.milestone
        heading = fit_small(event.sport.upper() + ' OPENING', 62)
        small(fb, heading, 1, 1, (239, 195, 95))
        label = str(self.result.days) + 'D'
        fb.text(label, max(0, (64 - (len(label) * 6 - 1)) // 2), 11, (240, 240, 235))
        sub = f'{self.result.hours:02d}H {self.result.minutes:02d}M'
        sub = fit_small(sub, 62)
        small(fb, sub, small_center_x(sub), 23, (115, 155, 185))
        return fb
