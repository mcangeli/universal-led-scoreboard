"""64x32 standalone clock screen. Never requires a network connection."""
from dataclasses import dataclass
from datetime import datetime
from zoneinfo import ZoneInfo

from .display import Framebuffer
from .mlb_classic import small


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
        small(frame, date_label[:16], 0, 1, gold)
        value = now.strftime('%I:%M' if self.time_format == '12h' else '%H:%M')
        if self.time_format == '12h':
            value = value.lstrip('0') or '0'
        # Large 5x7 numerals occupy the center of the 64x32 display.
        x = max(0, (64 - (len(value) * 6 - 1)) // 2)
        frame.text(value, x, 12, white)
        if self.time_format == '12h':
            small(frame, now.strftime('%p'), 27, 25, muted)
        else:
            small(frame, now.strftime('%a').upper(), 26, 25, muted)
        return frame
