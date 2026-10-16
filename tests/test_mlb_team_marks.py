import unittest
from universal_led.display import Framebuffer
from universal_led.mlb_classic import BaseballGame
from universal_led.mlb_palette_v11 import MLBPaletteScreen
from universal_led.mlb_team_marks import draw_team_mark, MARKS, SPRITES

class MLBTeamMarksTests(unittest.TestCase):
    def test_known_and_unknown_marks(self):
        frame = Framebuffer()
        self.assertTrue(draw_team_mark(frame, 'ATL', 25, 7))
        self.assertTrue(draw_team_mark(frame, 'PHI', 25, 17))
        self.assertFalse(draw_team_mark(frame, 'ZZZ', 25, 7))
        self.assertNotEqual(frame.pixels[7][25], (0, 0, 0))

    def test_all_thirty_clubs_have_marks(self):
        clubs = ('ARI ATL BAL BOS CHC CIN CLE COL CWS DET HOU KCR LAA LAD MIA MIL MIN NYM NYY ATH PHI PIT SDP SEA SFG STL TBR TEX TOR WSH').split()
        self.assertEqual(len(clubs), 30)
        self.assertTrue(set(clubs).issubset(MARKS))
        for team in clubs:
            with self.subTest(team=team):
                frame = Framebuffer()
                self.assertTrue(draw_team_mark(frame, team, 25, 7))
                self.assertTrue(any(pixel != (0, 0, 0) for row in frame.pixels[7:14] for pixel in row[25:34]))

    def test_custom_sprites_are_transparent_and_fit(self):
        self.assertEqual(set(SPRITES), {'MIL', 'LAD'})
        for team, rows in SPRITES.items():
            with self.subTest(team=team):
                self.assertEqual(len(rows), 7)
                self.assertTrue(all(len(row) == 9 for row in rows))
                frame = Framebuffer()
                self.assertTrue(draw_team_mark(frame, team, 25, 7))
                self.assertEqual(frame.pixels[7][25], (0, 0, 0))
                self.assertTrue(any(pixel != (0, 0, 0)
                                    for row in frame.pixels[7:14]
                                    for pixel in row[25:34]))
                self.assertTrue(all(pixel == (0, 0, 0)
                                    for row in frame.pixels[7:14]
                                    for pixel in row[34:42]))

    def test_custom_sprites_render_on_live_classic(self):
        game = BaseballGame(away='MIL', home='LAD')
        live = MLBPaletteScreen(game).render()
        final = MLBPaletteScreen(BaseballGame(away='MIL', home='LAD', status='final')).render()
        self.assertEqual(live.pixels[7][25], (0, 0, 0))
        self.assertNotEqual(live.pixels[7][28], (0, 0, 0))
        self.assertEqual(final.pixels[7][28], (0, 0, 0))

    def test_marks_only_on_live_classic(self):
        live = MLBPaletteScreen(BaseballGame(away='PHI', home='ATL')).render()
        final = MLBPaletteScreen(BaseballGame(away='PHI', home='ATL', status='final')).render()
        self.assertNotEqual(live.pixels[7][25], (0, 0, 0))
        self.assertEqual(final.pixels[7][25], (0, 0, 0))
        self.assertEqual(live.pixels[25][25], live.pixels[25][0])

if __name__ == '__main__':
    unittest.main()
