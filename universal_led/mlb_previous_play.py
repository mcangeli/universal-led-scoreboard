"""Scrolling 64x32 play-description screen for live MLB games."""
from dataclasses import dataclass, field
from .display import Framebuffer
from .mlb_classic import BaseballGame, SMALL, small
from .colors import load_palette


def sanitize_play(text):
    return ''.join(ch if ch in SMALL else ' ' for ch in (text or '').replace('’', "'").replace('‘', "'").upper())



def wrap_play(text, width=16):
    """Wrap at word boundaries; split only tokens wider than a full row."""
    words=sanitize_play(text).split()
    lines=[]
    current=''
    for word in words:
        while len(word)>width:
            if current:
                lines.append(current)
                current=''
            lines.append(word[:width])
            word=word[width:]
        if not word:
            continue
        if not current:
            current=word
        elif len(current)+1+len(word)<=width:
            current+=' '+word
        else:
            lines.append(current)
            current=word
    if current:
        lines.append(current)
    return lines or ['NO PLAY DATA']


def visible_play_lines(text, offset=0, width=16):
    """Show two complete wrapped rows; offset is a character-based scroll clock."""
    lines=wrap_play(text,width)
    if len(lines)<=2:
        return (lines+[''])[:2]
    # The animation clock advances in glyphs. Convert that to row starts
    # so scrolling never begins in the middle of a word.
    starts=[]
    position=0
    for line in lines:
        starts.append(position)
        position+=len(line)+1
    index=0
    for i,start in enumerate(starts):
        if start<=max(0,offset):
            index=i
        else:
            break
    index=min(index,len(lines)-2)
    return lines[index:index+2]

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
        first,second=visible_play_lines(self.game.previous_play,self.offset)
        small(fb,first,0,12,c['text'])
        small(fb,second,0,20,c['text'])
        return fb
