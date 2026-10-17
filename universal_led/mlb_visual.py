"""Preview 8: 64x32 MLB presentation with team accents and status labels.

Team accent colors are approximate LED-friendly palette choices, not licensed art.
"""
from dataclasses import dataclass
from .mlb_refined import MLBRefinedScreen
from .mlb_classic import BaseballGame, small, GOLD, DIM, RED

TEAM_COLORS = {
    'ATL':(206,32,54),'NYM':(245,128,38),'NYY':(100,130,178),
    'BOS':(189,48,65),'LAD':(38,113,205),'SDP':(206,166,77),
    'PHI':(220,49,70),'CHC':(45,106,196),'MIL':(210,164,76),
    'HOU':(232,114,39),'SEA':(49,168,163),'TOR':(50,112,210),
    'CLE':(204,54,66),'DET':(111,149,194),'MIN':(193,49,70),
    'CWS':(180,180,180),'KCR':(62,123,219),'BAL':(236,117,43),
    'TBR':(98,164,209),'TEX':(53,104,205),'OAK':(59,148,97),
    'LAA':(208,46,62),'SFG':(234,111,51),'ARI':(186,58,69),
    'COL':(144,109,174),'STL':(210,42,66),'CIN':(224,46,62),
    'PIT':(241,191,64),'WSN':(201,48,64),'MIA':(66,163,205)
}

@dataclass(frozen=True)
class MLBVisualScreen:
    game: BaseballGame = BaseballGame()
    name: str = 'mlb-visual'
    def render(self):
        from .colors import readable_on_black
        g = self.game
        fb = MLBRefinedScreen(g).render()
        # Replace generic team labels with team-specific color.
        for y in list(range(7,14)) + list(range(17,24)):
            for x in range(1,19):
                fb.pixel(x,y,(0,0,0))
        fb.text(g.away,1,7,readable_on_black(TEAM_COLORS.get(g.away,(225,225,225))))
        fb.text(g.home,1,17,readable_on_black(TEAM_COLORS.get(g.home,(225,225,225))))
        if g.status == 'delayed':
            small(fb,'DELAY',2,27,GOLD)
        elif g.status == 'postponed':
            small(fb,'PPD',2,27,RED)
        elif g.status == 'pregame':
            small(fb,'PM',2,27,GOLD)
        return fb
