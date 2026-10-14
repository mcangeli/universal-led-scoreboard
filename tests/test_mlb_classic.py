import unittest
from universal_led.mlb_classic import BaseballGame, MLBClassicScreen, GOLD

class MLBClassicTests(unittest.TestCase):
    def test_render_native_64x32(self):
        frame=MLBClassicScreen().render()
        self.assertEqual((frame.width,frame.height),(64,32))
        self.assertEqual(len(frame.pixels),32)
        self.assertTrue(all(len(row)==64 for row in frame.pixels))
    def test_all_statuses_render(self):
        for status in ('live','pregame','final'):
            with self.subTest(status=status):
                frame=MLBClassicScreen(BaseballGame(status=status)).render()
                self.assertTrue(any(any(channel for channel in p) for row in frame.pixels for p in row))
    def test_bases_and_outs(self):
        frame=MLBClassicScreen().render()
        self.assertEqual(frame.pixels[27][34],(110,125,140))
        self.assertEqual(frame.pixels[29][38],GOLD)
        self.assertEqual(frame.pixels[29][30],GOLD)  # third base is occupied
        self.assertEqual(frame.pixels[29][14],(240,80,70))  # first out is lit
    def test_double_digit_scores(self):
        frame=MLBClassicScreen(BaseballGame(away_runs=12,home_runs=15)).render()
        self.assertTrue(any(p!=(0,0,0) for p in frame.pixels[9][38:50]))
    def test_invalid_fixture(self):
        with self.assertRaises(ValueError):
            BaseballGame(outs=4)
        with self.assertRaises(ValueError):
            BaseballGame(away='NEW YORK')
if __name__=='__main__':
    unittest.main()
