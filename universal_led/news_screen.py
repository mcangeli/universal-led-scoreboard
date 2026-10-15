"""Compact 64x32 headline card with word-safe two-row paging."""
from dataclasses import dataclass
from .display import Framebuffer
from .mlb_classic import small
from .mlb_previous_play import sanitize_play, wrap_play


def headline_page(headline, offset=0):
    lines = wrap_play(headline, width=16)
    if len(lines) <= 2:
        return (lines + [''])[:2]
    index = max(0, int(offset)) // 16 % (len(lines) - 1)
    return lines[index:index + 2]


@dataclass(frozen=True)
class NewsHeadlineScreen:
    headline: str
    source: str = 'NEWS'
    offset: int = 0

    def render(self):
        frame = Framebuffer(64, 32)
        accent = (239, 195, 95)
        ink = (235, 235, 225)
        label = sanitize_play(self.source)[:15]
        small(frame, label or 'NEWS', 1, 1, accent)
        for x in range(64):
            frame.pixel(x, 8, (85, 100, 115))
        first, second = headline_page(self.headline, self.offset)
        small(frame, first, 0, 13, ink)
        small(frame, second, 0, 22, ink)
        return frame
