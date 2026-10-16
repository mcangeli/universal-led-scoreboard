import unittest
from universal_led.display import Framebuffer
from universal_led.mlb_classic import BaseballGame
from universal_led.mlb_palette_v11 import MLBPaletteScreen
from universal_led.mlb_team_marks import draw_team_mark

class MLBTeamMarksTests(unittest.TestCase):
    def test_known_and_unknown_marks(self):
        frame = Framebuffer()
        self.assertTrue(draw_team_mark(frame, 'ATL', 25, 7))
        self.assertTrue(draw_team_mark(frame, 'PHI', 25, 17))
        self.assertFalse(draw_team_mark(frame, 'NYM', 25, 7))
        self.assertNotEqual(frame.pixels[7][25], (0, 0, 0))

    def test_marks_only_on_live_classic(self):
        live = MLBPaletteScreen(BaseballGame(away='PHI', home='ATL')).render()
        final = MLBPaletteScreen(BaseballGame(away='PHI', home='ATL', status='final')).render()
        self.assertNotEqual(live.pixels[7][25], (0, 0, 0))
        self.assertEqual(final.pixels[7][25], (0, 0, 0))
        self.assertEqual(live.pixels[25][25], live.pixels[25][0])

if __name__ == '__main__':
    unittest.main()
