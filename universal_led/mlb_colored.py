"""Preview 10: configurable MLB colors with native 64x32 rendering."""
from dataclasses import dataclass,field
from .mlb_classic import BaseballGame,small
from .mlb_classic_v9 import MLBClassicV9Screen
from .colors import load_palette

@dataclass(frozen=True)
class MLBColoredScreen:
    game: BaseballGame=BaseballGame()
    team_colors: dict=field(default_factory=lambda:load_palette()[0])
    scoreboard_colors: dict=field(default_factory=lambda:load_palette()[1])
    name: str='mlb-colored'

    def render(self):
        g=self.game
        fb=MLBClassicV9Screen(g).render()
        # Overwrite the two team-label regions with configured colors.
        for y,team in ((7,g.away),(17,g.home)):
            for yy in range(y,y+7):
                for xx in range(1,19):
                    fb.pixel(xx,yy,(0,0,0))
            fb.text(team,1,y,self.team_colors.get(team,self.scoreboard_colors['text']))
        # Global scoreboard palette applies to R/H/E header and separator.
        for x in range(64):
            fb.pixel(x,25,self.scoreboard_colors['separator'])
        for right in (46,54,62):
            for yy in range(1,6):
                for xx in range(right-2,right+1):
                    if fb.pixels[yy][xx]!=(0,0,0):
                        fb.pixel(xx,yy,self.scoreboard_colors['accent'])
        return fb
