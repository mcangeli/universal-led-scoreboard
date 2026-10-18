import unittest
from universal_led.mlb_classic import BaseballGame
from universal_led.colors import load_palette
from universal_led.mlb_palette_v11 import MLBPaletteScreen

class PaletteV11Tests(unittest.TestCase):
    def setUp(self):
        self.teams,self.colors=load_palette()
        self.colors.update({'text':(1,2,3),'dim':(4,5,6),
                            'accent':(7,8,9),'error':(10,11,12),
                            'separator':(13,14,15)})
    def screen(self,game=None):
        return MLBPaletteScreen(game or BaseballGame(),self.teams,self.colors).render()
    def test_dimensions(self):
        f=self.screen()
        self.assertEqual((f.width,f.height),(64,32))
    def test_score_and_header(self):
        f=self.screen()
        self.assertIn((1,2,3),f.pixels[8])
        self.assertIn((7,8,9),f.pixels[1])
    def test_separator(self):
        self.assertEqual(self.screen().pixels[25][0],(13,14,15))
    def test_outs_and_bases(self):
        f=self.screen()
        self.assertEqual(f.pixels[28][20],(10,11,12))
        self.assertEqual(f.pixels[28][24],(0,0,0))
        self.assertEqual(f.pixels[27][23],(4,5,6))
        self.assertEqual(f.pixels[29][45],(7,8,9))
        self.assertEqual(f.pixels[27][50],(4,5,6))
    def test_status_colors(self):
        for status in ('delayed','postponed'):
            with self.subTest(status=status):
                f=self.screen(BaseballGame(status=status))
                self.assertIn((10,11,12),f.pixels[27])
    def test_double_digit_totals_have_clear_column_gutters(self):
        f = self.screen(BaseballGame(away_runs=31, away_hits=11,
                                     away_errors=0, home_runs=12,
                                     home_hits=15, home_errors=10))
        for y in (8, 18):
            for x in (42, 43, 44, 52, 53, 54):
                with self.subTest(x=x, y=y):
                    self.assertTrue(all(f.pixels[row][x] == (0, 0, 0)
                                        for row in range(y, y+5)))
        for y in (8, 18):
            for start in (35, 45, 55):
                self.assertTrue(any(f.pixels[row][x] == (1, 2, 3)
                                    for row in range(y, y+5)
                                    for x in range(start, start+7)))

    def test_large_stats(self):
        f=self.screen(BaseballGame(away_runs=100))
        self.assertEqual(f.pixels[9][36],(10,11,12))

if __name__=='__main__':
    unittest.main()
