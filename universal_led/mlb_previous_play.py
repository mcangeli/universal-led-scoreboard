"""Scrolling 64x32 play-description screen for live MLB games."""
from dataclasses import dataclass, field
from .display import Framebuffer
from .mlb_classic import BaseballGame, SMALL, small
from .colors import load_palette


def sanitize_play(text):
    return ''.join(ch if ch in SMALL else ' ' for ch in (text or '').upper())


@dataclass(frozen=True)
class MLBPreviousPlayScreen:
    game: BaseballGame
    offset: int = 0
    scoreboard_colors: dict = field(default_factory=lambda: load_palette()[1])
    name: str = 'mlb-previous-play'

    def render(self):
        c=self.scoreboard_colors
        fb=Framebuffer(64,32)
        small(fb,'LAST PLAY',1,1,c['accent'])
        for x in range(64):
            fb.pixel(x,7,c['separator'])
        message=sanitize_play(self.game.previous_play) or 'NO PLAY DATA'
        # Render the scrolling text as two compact lines. Offset is measured
        # in glyphs, making animation independent of the frame rate.
        padded=' ' * 16 + message + ' ' * 16
        offset=max(0,min(self.offset,max(0,len(padded)-16)))
        visible=padded[offset:offset+32].ljust(32)
        small(fb,visible[:16],0,12,c['text'])
        small(fb,visible[16:],0,20,c['text'])
        return fb
