"""64x32 standalone clock screen. Never requires a network connection."""
from dataclasses import dataclass
from datetime import datetime
from zoneinfo import ZoneInfo

from .display import Framebuffer
from .mlb_classic import small
from .safe_layout import MARGIN, fit_small, big_center_x, small_center_x


@dataclass(frozen=True)
class ClockScreen:
    timezone: str = 'America/New_York'
    time_format: str = '12h'
    now: datetime | None = None

    def render(self):
        now = (self.now or datetime.now(ZoneInfo(self.timezone))).astimezone(ZoneInfo(self.timezone))
        frame = Framebuffer(64, 32)
        gold = (239, 195, 95)
        white = (235, 235, 225)
        muted = (120, 140, 155)
        date_label = now.strftime('%a %b %d').upper()
        small(frame, fit_small(date_label, 60), MARGIN, MARGIN, gold)
        value = now.strftime('%I:%M' if self.time_format == '12h' else '%H:%M')
        if self.time_format == '12h':
            value = value.lstrip('0') or '0'
        # Large 5x7 numerals occupy the center of the 64x32 display.
        x = big_center_x(value)
        frame.text(value, x, 12, white)
        if self.time_format == '12h':
            label=now.strftime('%p')
            small(frame, label, small_center_x(label), 25, muted)
        else:
            label=now.strftime('%a').upper()
            small(frame, label, small_center_x(label), 25, muted)
        return frame
