"""Final-score winner indicator and 64x32 layout regressions."""
import unittest
from universal_led.mlb_classic import BaseballGame
from universal_led.mlb_palette_v11 import MLBPaletteScreen

COLORS={'text':(1,2,3),'dim':(4,5,6),'accent':(7,8,9),
        'error':(10,11,12),'separator':(13,14,15)}

class FinalScoreTests(unittest.TestCase):
    def render(self, **kwargs):
        return MLBPaletteScreen(BaseballGame(**kwargs),scoreboard_colors=COLORS).render()

    def test_winning_team_marker_home_and_away(self):
        for away,home,winner_y,loser_y in ((5,2,8,18),(2,5,18,8)):
            with self.subTest(away=away,home=home):
                frame=self.render(status='final',away_runs=away,home_runs=home)
                for dx,dy in ((0,0),(1,1),(0,2)):
                    self.assertEqual(frame.pixels[winner_y+dy][24+dx],COLORS['accent'])
                    self.assertEqual(frame.pixels[loser_y+dy][24+dx],(0,0,0))

    def test_tie_and_live_do_not_mark_winner(self):
        for status,away,home in (('final',2,2),('live',5,2),('pregame',0,0)):
            with self.subTest(status=status):
                frame=self.render(status=status,away_runs=away,home_runs=home)
                self.assertEqual(frame.pixels[8][24],(0,0,0))
                self.assertEqual(frame.pixels[18][24],(0,0,0))

    def test_final_in_extra_innings_retains_winner_marker(self):
        frame=self.render(status='final',inning=12,away_runs=11,home_runs=10)
        self.assertEqual(frame.pixels[8][24],COLORS['accent'])
        self.assertTrue(any(pixel==COLORS['dim'] for row in frame.pixels[27:32] for pixel in row))
        self.assertEqual((frame.width,frame.height),(64,32))

if __name__=='__main__':
    unittest.main()
