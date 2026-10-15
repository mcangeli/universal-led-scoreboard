import unittest
from universal_led.mlb_classic import BaseballGame
from universal_led.mlb_palette_v11 import MLBPaletteScreen

class LiveFinalParityTests(unittest.TestCase):
    def test_double_digit_inning_arrow_does_not_overlap_number(self):
        colors={'text':(1,2,3),'dim':(4,5,6),'accent':(7,8,9),
                'error':(10,11,12),'separator':(13,14,15)}
        for inning, arrow_x in ((9,12),(10,16),(12,16)):
            for half, arrow_y in (('top',27),('bottom',31)):
                with self.subTest(inning=inning,half=half):
                    game=BaseballGame(inning=inning,inning_half=half)
                    frame=MLBPaletteScreen(game,scoreboard_colors=colors).render()
                    self.assertEqual(frame.pixels[arrow_y][arrow_x],colors['accent'])
                    self.assertEqual((frame.width,frame.height),(64,32))

    def test_extra_inning_final_has_inning_number(self):
        colors={'text':(1,2,3),'dim':(4,5,6),'accent':(7,8,9),
                'error':(10,11,12),'separator':(13,14,15)}
        extra=MLBPaletteScreen(BaseballGame(status='final',inning=12),scoreboard_colors=colors).render()
        normal=MLBPaletteScreen(BaseballGame(status='final',inning=9),scoreboard_colors=colors).render()
        self.assertNotEqual(extra.pixels[27:32],normal.pixels[27:32])
        self.assertTrue(any(p==colors['dim'] for row in extra.pixels[27:32] for p in row))

    def test_double_digit_stats_and_base_occupancy(self):
        frame=MLBPaletteScreen(BaseballGame(away_runs=12,home_runs=10,
                away_hits=15,home_hits=13,bases=(True,True,True),outs=2)).render()
        self.assertEqual((frame.width,frame.height),(64,32))

if __name__=='__main__':
    unittest.main()
