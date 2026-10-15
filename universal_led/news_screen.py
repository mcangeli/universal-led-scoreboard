"""Compact 64x32 headline card with word-safe two-row paging."""
from dataclasses import dataclass
from .display import Framebuffer
from .mlb_classic import small
from .mlb_previous_play import sanitize_play, visible_play_lines


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
        first, second = visible_play_lines(self.headline, self.offset, width=16)
        small(frame, first, 0, 13, ink)
        small(frame, second, 0, 22, ink)
        return frame
