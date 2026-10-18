"""Optional 64x32 MLB matchup page, shown only when live details exist."""
from dataclasses import dataclass, field
from .mlb_classic import BaseballGame, SMALL, small
from .display import Framebuffer
from .colors import load_palette


def compact_name(value):
    """Return a display-safe surname without silently truncating long names."""
    if not value or not value.strip():
        return 'TBD'
    parts=value.strip().split()
    # Preserve common surname particles rather than displaying only the last word.
    particles={'DE','DEL','DELA','DE','VAN','VON','DA','DOS','DI','LA','LE'}
    start=len(parts)-1
    while start>0 and parts[start-1].upper() in particles:
        start-=1
    name=' '.join(parts[start:]).upper()
    return ''.join(ch if ch in SMALL else ' ' for ch in name).strip() or 'TBD'


def visible_name(value, offset=0, width=13):
    name=compact_name(value)
    if len(name)<=width:
        return name
    # Wrap through the name with a short readable gap; never draw beyond x=63.
    cycle=name+'   '
    offset=max(0,int(offset))%len(cycle)
    repeated=cycle*3
    return repeated[offset:offset+width]


@dataclass(frozen=True)
class MLBLiveDetailsScreen:
    game: BaseballGame
    scoreboard_colors: dict = field(default_factory=lambda: load_palette()[1])
    name: str = 'mlb-live-details'
    offset: int = 0

    def render(self):
        g=self.game
        c=self.scoreboard_colors
        fb=Framebuffer(64,32)
        small(fb,'MATCHUP',1,1,c['accent'])
        for x in range(64):
            fb.pixel(x,7,c['separator'])
        small(fb,'P',1,10,c['accent'])
        small(fb,visible_name(g.pitcher,self.offset),9,10,c['text'])
        small(fb,'B',1,18,c['accent'])
        small(fb,visible_name(g.batter,self.offset),9,18,c['text'])
        for x in range(64):
            fb.pixel(x,25,c['separator'])
        balls='-' if g.balls is None else str(g.balls)
        strikes='-' if g.strikes is None else str(g.strikes)
        small(fb,'B '+balls+' S '+strikes,2,27,c['text'])
        if g.pitch_count is not None:
            small(fb,'P'+str(min(g.pitch_count,999)),32,27,c['accent'])
        if g.pitch_speed_mph is not None:
            speed=str(round(g.pitch_speed_mph))
            small(fb,speed[:3],52,27,c['text'])
        return fb
