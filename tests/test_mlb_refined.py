import unittest
from universal_led.mlb_refined import MLBRefinedScreen
from universal_led.mlb_classic import BaseballGame, GOLD, DIM, RED

class MLBRefinedTests(unittest.TestCase):
    def test_dimensions(self):
        f=MLBRefinedScreen().render()
        self.assertEqual((f.width, f.height),(64,32))
        self.assertEqual(len(f.pixels),32)
        self.assertTrue(all(len(row)==64 for row in f.pixels))
    def test_bases(self):
        f=MLBRefinedScreen().render()
        self.assertEqual(f.pixels[29][45],GOLD)  # third occupied
        self.assertEqual(f.pixels[29][55],GOLD)  # first occupied
        self.assertEqual(f.pixels[27][50],DIM)   # second empty
    def test_outs(self):
        f=MLBRefinedScreen().render()
        self.assertEqual(f.pixels[28][20],RED)
        self.assertEqual(f.pixels[28][24],DIM)
    def test_all_statuses(self):
        for status in ('live','final','pregame'):
            with self.subTest(status=status):
                f=MLBRefinedScreen(BaseballGame(status=status)).render()
                self.assertEqual(len(f.pixels),32)
    def test_two_digit_stats(self):
        f=MLBRefinedScreen(BaseballGame(away_runs=12,home_runs=14,away_hits=17)).render()
        self.assertTrue(any(f.pixels[8][x] != (0,0,0) for x in range(39,47)))
    def test_large_stat_indicators(self):
        f=MLBRefinedScreen(BaseballGame(away_runs=100)).render()
        self.assertEqual(f.pixels[9][40],RED)

if __name__=='__main__':
    unittest.main()
