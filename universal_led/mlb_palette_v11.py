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

    def render(self) -> Framebuffer:
        g=self.game
        c=self.scoreboard_colors
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
            small(fb,'FINAL',2,27,c['accent'])
        elif g.status=='delayed':
            small(fb,'DELAY',2,27,c['error'])
        elif g.status=='postponed':
            small(fb,'PPD',2,27,c['error'])
        else:
            small(fb,str(min(g.inning,99)),2,27,c['accent'])
            top=g.inning_half=='top'
            fb.pixel(12,27 if top else 31,c['accent'])
            fb.pixel(11,28 if top else 30,c['accent'])
            fb.pixel(13,28 if top else 30,c['accent'])
            for i in range(3):
                for y in (28,29):
                    fb.pixel(20+i*4,y,c['error'] if i<g.outs else c['dim'])
            for x,y,on in ((50,27,g.bases[1]),(45,29,g.bases[2]),(55,29,g.bases[0])):
                color=c['accent'] if on else c['dim']
                for dx,dy in ((0,0),(-1,0),(1,0),(0,1)):
                    fb.pixel(x+dx,y+dy,color)
        return fb
