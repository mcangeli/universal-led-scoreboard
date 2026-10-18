"""Preview 5: carefully bounded 64x32 baseball layout, using offline fixtures."""
from dataclasses import dataclass
from .display import Framebuffer
from .mlb_classic import BaseballGame, small, WHITE, DIM, GOLD, GREEN, RED

@dataclass(frozen=True)
class MLBRefinedScreen:
    game: BaseballGame = BaseballGame()
    name: str = 'mlb-refined'

    def render(self) -> Framebuffer:
        g = self.game
        fb = Framebuffer(64, 32)
        # Main rows: team names at left, score totals at right.
        # 5x7 labels occupy x=1..17. Compact 3x5 stats occupy x=39..62.
        small(fb, 'MLB', 1, 1, GOLD)
        small(fb, 'R H E'.replace(' ', ''), 43, 1, GOLD)
        fb.text(g.away, 1, 7, WHITE)
        fb.text(g.home, 1, 17, GREEN)
        for y, stats in ((8, (g.away_runs, g.away_hits, g.away_errors)),
                         (18, (g.home_runs, g.home_hits, g.home_errors))):
            for right, value in zip((40, 50, 60), stats):
                # Each 8-pixel slot fits two 3x5 digits; don't silently truncate.
                label = str(value) if value < 100 else '++'
                if label == '++':
                    # Mark values beyond representable range with two lit bars.
                    for x in (right-6, right-2):
                        for yy in (y+1, y+3):
                            fb.pixel(x, yy, RED)
                else:
                    small(fb, label, right - (len(label)*4-1), y, WHITE)
        # A separator preserves visual hierarchy between scores and game state.
        for x in range(64):
            fb.pixel(x, 25, (28, 37, 48))
        if g.status == 'final':
            small(fb, 'FINAL', 2, 27, GOLD)
        elif g.status == 'pregame':
            small(fb, 'PM', 2, 27, GOLD)
        else:
            # Bottom strip: inning, half, outs, and three base markers.
            inning = str(g.inning)
            small(fb, inning if len(inning) <= 2 else '99', 2, 27, GOLD)
            # Arrow direction: top = up, bottom = down.
            arrow_y = 27 if g.inning_half == 'top' else 31
            fb.pixel(12, arrow_y, GOLD)
            fb.pixel(11, 28 if g.inning_half == 'top' else 30, GOLD)
            fb.pixel(13, 28 if g.inning_half == 'top' else 30, GOLD)
            for i in range(3):
                for yy in (28, 29):
                    fb.pixel(20 + i*4, yy, RED if i < g.outs else DIM)
            # Small but distinct diamond, x=44..56; second, third, first.
            for x,y,occupied in ((50,27,g.bases[1]),
                                 (45,29,g.bases[2]),
                                 (55,29,g.bases[0])):
                color = GOLD if occupied else DIM
                fb.pixel(x,y,color)
                fb.pixel(x-1,y,color)
                fb.pixel(x+1,y,color)
                fb.pixel(x,y+1,color)
        return fb
