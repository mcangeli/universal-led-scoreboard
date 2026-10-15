import unittest
from universal_led.mlb_classic import BaseballGame, SMALL
from universal_led.mlb_palette_v11 import MLBPaletteScreen
from universal_led.mlb_classic_v9 import MLBClassicV9Screen

class PregameStatusTests(unittest.TestCase):
    def test_full_pregame_label_fits_status_strip(self):
        self.assertTrue(all(ch in SMALL for ch in 'PREGAME'))
        self.assertLessEqual(2 + 4 * len('PREGAME'), 64)

    def test_missing_time_renders_without_crashing(self):
        for screen in (MLBPaletteScreen, MLBClassicV9Screen):
            with self.subTest(screen=screen.__name__):
                frame = screen(BaseballGame(status='pregame', start_time=None)).render()
                self.assertEqual((frame.width, frame.height), (64, 32))
                self.assertTrue(any(any(channel for channel in pixel)
                                    for row in frame.pixels[27:] for pixel in row))

    def test_valid_time_renders(self):
        frame = MLBPaletteScreen(BaseballGame(status='pregame', start_time='2026-10-15T19:30:00Z')).render()
        self.assertEqual((frame.width, frame.height), (64, 32))

if __name__ == '__main__':
    unittest.main()
