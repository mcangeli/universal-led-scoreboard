"""Preview 9: compact classic-inspired 64x32 MLB layout.

Original artwork is not copied. Header, score columns and status strip are
laid out explicitly to avoid overlapping pixels.
"""
from dataclasses import dataclass
from datetime import datetime
from .display import Framebuffer
from .mlb_classic import BaseballGame, small, WHITE, DIM, GOLD, RED
from .mlb_visual import TEAM_COLORS

def start_label(iso: str | None) -> str:
    if not iso:
        return 'PREGAME'
    try:
        stamp = datetime.fromisoformat(iso.replace('Z','+00:00')).astimezone()
        return stamp.strftime('%I%M%p').lstrip('0')
    except (ValueError, TypeError, OverflowError):
        return 'PREGAME'

@dataclass(frozen=True)
class MLBClassicV9Screen:
    game: BaseballGame = BaseballGame()
    name: str = 'mlb-classic-v9'

    def render(self) -> Framebuffer:
        g = self.game
        fb = Framebuffer(64,32)
        # Each numeric column has 8px: x=40..46, 48..54, 56..62.
        # Headers centered on the same right edges as their values.
        for letter,right in zip('RHE',(46,54,62)):
            small(fb,letter,right-2,1,GOLD)
        for y,team,stats in (
            (8,g.away,(g.away_runs,g.away_hits,g.away_errors)),
            (18,g.home,(g.home_runs,g.home_hits,g.home_errors))):
            fb.text(team,1,y-1,TEAM_COLORS.get(team,WHITE))
            for right,value in zip((46,54,62),stats):
                if value >= 100:
                    for x in (right-6,right-2):
                        fb.pixel(x,y+1,RED)
                        fb.pixel(x,y+3,RED)
                else:
                    digits=str(value)
                    small(fb,digits,right-(len(digits)*4-1),y,WHITE)
        for x in range(64):
            fb.pixel(x,25,(28,37,48))
        if g.status == 'pregame':
            label=start_label(g.start_time)
            # Compact glyphs lack punctuation; render clock digits + AM/PM.
            if label == 'PREGAME':
                small(fb,'PM',2,27,GOLD)
            else:
                small(fb,label[:9],2,27,GOLD)
        elif g.status == 'final':
            small(fb,'FINAL',2,27,GOLD)
        elif g.status == 'delayed':
            small(fb,'DELAY',2,27,GOLD)
        elif g.status == 'postponed':
            small(fb,'PPD',2,27,RED)
        else:
            digits=str(min(g.inning,99))
            small(fb,digits,2,27,GOLD)
            # inning direction, outs, and 1B/2B/3B markers
            top=g.inning_half=='top'
            fb.pixel(12,27 if top else 31,GOLD)
            fb.pixel(11,28 if top else 30,GOLD)
            fb.pixel(13,28 if top else 30,GOLD)
            for i in range(3):
                for y in (28,29):
                    fb.pixel(20+i*4,y,RED if i<g.outs else DIM)
            for x,y,on in ((50,27,g.bases[1]),(45,29,g.bases[2]),(55,29,g.bases[0])):
                color=GOLD if on else DIM
                for dx,dy in ((0,0),(-1,0),(1,0),(0,1)):
                    fb.pixel(x+dx,y+dy,color)
        return fb
