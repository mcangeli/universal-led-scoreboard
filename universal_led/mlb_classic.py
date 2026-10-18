"""64x32 MLB-inspired inning scoreboard. Offline fixtures; no live feed yet.

Independent clean-room layout: this is not a port of upstream MLB artwork.
"""
from dataclasses import dataclass
from typing import Literal
from .display import Framebuffer

Status = Literal['live', 'pregame', 'final', 'delayed', 'postponed']
WHITE=(235,235,225)
DIM=(110,125,140)
GOLD=(239,195,95)
GREEN=(80,205,105)
RED=(240,80,70)

# 3x5 glyphs for compact score labels; 4px advance.
SMALL={
'0':('111','101','101','101','111'),
'1':('010','110','010','010','111'),
'2':('111','001','111','100','111'),
'3':('111','001','111','001','111'),
'4':('101','101','111','001','001'),
'5':('111','100','111','001','111'),
'6':('111','100','111','101','111'),
'7':('111','001','010','010','010'),
'8':('111','101','111','101','111'),
'9':('111','101','111','001','111'),
'R':('110','101','110','101','101'),
'H':('101','101','111','101','101'),
'E':('111','100','110','100','111'),
'I':('111','010','010','010','111'),
'N':('101','111','111','111','101'),
'F':('111','100','110','100','100'),
'G':('111','100','101','101','111'),
'B':('110','101','110','101','110'),
'C':('111','100','100','100','111'),
'K':('101','101','110','101','101'),
'W':('101','101','111','111','101'),
'J':('001','001','001','101','111'),
'Q':('111','101','101','111','001'),
'U':('101','101','101','101','111'),
'V':('101','101','101','101','010'),
'X':('101','101','010','101','101'),
'Z':('111','001','010','100','111'),
'-':('000','000','111','000','000'),
'&':('010','101','010','101','011'),
'.':('000','000','000','000','010'),
'A':('010','101','111','101','101'),
'L':('100','100','100','100','111'),
'P':('110','101','110','100','100'),
'M':('101','111','111','101','101'),
'T':('111','010','010','010','010'),
'D':('110','101','101','101','110'),
'Y':('101','101','010','010','010'),
'S':('111','100','111','001','111'),
'O':('111','101','101','101','111'),
':':('000','110','000','110','000'),
' ':('000',)*5,
"'":('010','010','000','000','000'),
}
def small(fb: Framebuffer, text: str, x: int, y: int, color=WHITE):
    for i,ch in enumerate(text.upper()):
        for yy,bits in enumerate(SMALL[ch]):
            for xx,bit in enumerate(bits):
                if bit=='1': fb.pixel(x+4*i+xx,y+yy,color)

@dataclass(frozen=True)
class BaseballGame:
    away: str = 'NYM'
    home: str = 'ATL'
    away_runs: int = 2
    home_runs: int = 4
    away_hits: int = 5
    home_hits: int = 8
    away_errors: int = 0
    home_errors: int = 1
    inning: int = 7
    inning_half: Literal['top','bottom'] = 'bottom'
    inning_state: str | None = None  # MLB linescore: Top, Bottom, Middle, End
    outs: int = 1
    bases: tuple[bool,bool,bool] = (True,False,True)
    status: Status = 'live'
    start_time: str | None = None  # ISO 8601 gameDate from MLB schedule
    away_record: str | None = None
    home_record: str | None = None
    away_probable: str | None = None
    home_probable: str | None = None
    balls: int | None = None
    strikes: int | None = None
    pitcher: str | None = None
    batter: str | None = None
    pitch_count: int | None = None
    pitch_speed_mph: float | None = None
    previous_play: str | None = None
    game_pk: int | None = None
    def __post_init__(self):
        if self.balls is not None and self.balls not in range(5):
            raise ValueError('Invalid ball count')
        if self.strikes is not None and self.strikes not in range(4):
            raise ValueError('Invalid strike count')
        if self.pitch_count is not None and self.pitch_count < 0:
            raise ValueError('Invalid pitch count')
        if self.pitch_speed_mph is not None and self.pitch_speed_mph < 0:
            raise ValueError('Invalid pitch speed')
        if len(self.away)!=3 or len(self.home)!=3:
            raise ValueError('Three-letter team abbreviations required')
        if len(self.bases)!=3 or not all(type(b) is bool for b in self.bases):
            raise ValueError('Bases must be three booleans')
        if self.status not in ('live','pregame','final','delayed','postponed'):
            raise ValueError('Unknown game status')
        if self.inning < 1 or self.outs not in (0,1,2,3):
            raise ValueError('Invalid inning or outs')
        if min(self.away_runs,self.home_runs,self.away_hits,self.home_hits,
               self.away_errors,self.home_errors)<0:
            raise ValueError('Negative game statistics')

@dataclass(frozen=True)
class MLBClassicScreen:
    game: BaseballGame = BaseballGame()
    name: str = 'mlb-classic'
    def render(self) -> Framebuffer:
        g=self.game
        fb=Framebuffer(64,32)
        # Compact R/H/E grid on the right, teams on the left.
        small(fb,'MLB',1,1,GOLD)
        small(fb,'RHE',43,1,GOLD)
        fb.text(g.away.upper(),1,8,WHITE)
        fb.text(g.home.upper(),1,18,GREEN)
        for y,values in ((9,(g.away_runs,g.away_hits,g.away_errors)),
                         (19,(g.home_runs,g.home_hits,g.home_errors))):
            for x,value in zip((42,50,58),values):
                # Two-digit values stay within each column, using a 3px font.
                digits=str(value)
                if len(digits)>2: digits='99'
                small(fb,digits,x-(4 if len(digits)==2 else 0),y)
        if g.status=='live':
            small(fb,str(g.inning),1,27,GOLD)
            # Inning direction and outs: single pixels are legible on 64x32.
            fb.pixel(7,27 if g.inning_half=='top' else 31,GOLD)
            for i in range(3):
                fb.pixel(14+i*3,29,RED if i<g.outs else DIM)
            # Diamond: second, third, first, plus home anchor.
            for x,y,on in ((34,27,g.bases[1]),(30,29,g.bases[2]),(38,29,g.bases[0])):
                fb.pixel(x,y,GOLD if on else DIM)
        elif g.status=='final':
            small(fb,'FINAL',1,27,GOLD)
        else:
            small(fb,'PM',1,27,GOLD)
        return fb
