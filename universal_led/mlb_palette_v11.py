"""Preview 11: complete configurable color roles for MLB Classic 64x32."""
from dataclasses import dataclass, field
from .display import Framebuffer
from .mlb_classic import BaseballGame, small
from .mlb_classic_v9 import start_label, draw_start_label
from .colors import load_palette

@dataclass(frozen=True)
class MLBPaletteScreen:
    game: BaseballGame = BaseballGame()
    team_colors: dict = field(default_factory=lambda: load_palette()[0])
    scoreboard_colors: dict = field(default_factory=lambda: load_palette()[1])
    name: str = 'mlb-palette-v11'
    pregame_page: int = 0

    def _pregame_detail(self) -> Framebuffer:
        g=self.game
        c=self.scoreboard_colors
        fb=Framebuffer(64,32)
        page=self.pregame_page % 3
        small(fb,'STARTERS' if page==1 else 'RECORDS',1,1,c['accent'])
        for x in range(64):
            fb.pixel(x,7,c['separator'])
        for y,team,value in ((10,g.away,g.away_probable if page==1 else g.away_record),
                             (20,g.home,g.home_probable if page==1 else g.home_record)):
            small(fb,team,1,y,self.team_colors.get(team,c['text']))
            if page==1:
                # Names are shortened to last names to fit the 64-pixel matrix.
                # Preserve surname particles/hyphenation when possible; compact
                # text is deliberately clipped to the allotted 11 glyphs.
                label=(value or 'TBD').split()[-1]
            else:
                label=value or 'TBD'
            # Unsupported letters are replaced, not allowed to crash rendering.
            from .mlb_classic import SMALL
            label=''.join(ch if ch in SMALL else ' ' for ch in label.upper())[:11]
            small(fb,label,17,y,c['text'])
        return fb

    def render(self) -> Framebuffer:
        g=self.game
        c=self.scoreboard_colors
        if g.status == 'pregame' and self.pregame_page % 3:
            return self._pregame_detail()
        fb=Framebuffer(64,32)
        for label,right in zip('RHE',(46,54,62)):
            small(fb,label,right-2,1,c['accent'])
        for y,team,values in (
            (8,g.away,(g.away_runs,g.away_hits,g.away_errors)),
            (18,g.home,(g.home_runs,g.home_hits,g.home_errors))):
            fb.text(team,1,y-1,self.team_colors.get(team,c['text']))
            for right,value in zip((46,54,62),values):
                if value>=100:
                    for x in (right-6,right-2):
                        fb.pixel(x,y+1,c['error'])
                        fb.pixel(x,y+3,c['error'])
                else:
                    digits=str(value)
                    small(fb,digits,right-(len(digits)*4-1),y,c['text'])
        for x in range(64):
            fb.pixel(x,25,c['separator'])
        if g.status=='pregame':
            label=start_label(g.start_time)
            draw_start_label(fb,label,c['accent'],c['text'])
        elif g.status=='final':
            # Include inning count for extra-inning games without losing FINAL.
            small(fb,'FINAL',2,27,c['accent'])
            if g.inning>9:
                small(fb,str(min(g.inning,99)),34,27,c['dim'])
        elif g.status=='delayed':
            small(fb,'DELAY',2,27,c['error'])
        elif g.status=='postponed':
            small(fb,'PPD',2,27,c['error'])
        else:
            inning_label=str(min(g.inning,99))
            small(fb,inning_label,2,27,c['accent'])
            top=g.inning_half=='top'
            # Move direction arrow right when the inning reaches two digits.
            arrow_x=12 if len(inning_label)==1 else 16
            arrow_y=27 if top else 31
            fb.pixel(arrow_x,arrow_y,c['accent'])
            fb.pixel(arrow_x-1,28 if top else 30,c['accent'])
            fb.pixel(arrow_x+1,28 if top else 30,c['accent'])
            for i in range(3):
                for y in (28,29):
                    fb.pixel(20+i*4,y,c['error'] if i<g.outs else c['dim'])
            for x,y,on in ((50,27,g.bases[1]),(45,29,g.bases[2]),(55,29,g.bases[0])):
                color=c['accent'] if on else c['dim']
                for dx,dy in ((0,0),(-1,0),(1,0),(0,1)):
                    fb.pixel(x+dx,y+dy,color)
        return fb
