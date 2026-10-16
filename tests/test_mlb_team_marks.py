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
        self.assertTrue(any(pixel != (0, 0, 0) for row in frame.pixels[7:16] for pixel in row[24:36]))

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
        self.assertEqual(set(SPRITES), {'MIL', 'LAD', 'ATL', 'CLE', 'TBR'})
        for team, rows in SPRITES.items():
            with self.subTest(team=team):
                self.assertEqual(len(rows), 9)
                self.assertTrue(all(len(row) == 11 for row in rows))
                frame = Framebuffer()
                self.assertTrue(draw_team_mark(frame, team, 24, 6))
                area = [pixel for row in frame.pixels[6:15] for pixel in row[24:35]]
                self.assertIn((0, 0, 0), area)
                self.assertTrue(any(pixel != (0, 0, 0) for pixel in area))
                self.assertTrue(all(pixel == (0, 0, 0)
                                    for row in frame.pixels[6:15]
                                    for pixel in row[35:43]))

    def test_custom_sprites_render_on_live_classic(self):
        game = BaseballGame(away='MIL', home='LAD')
        live = MLBPaletteScreen(game).render()
        final = MLBPaletteScreen(BaseballGame(away='MIL', home='LAD', status='final')).render()
        self.assertEqual(live.pixels[6][24], (0, 0, 0))
        self.assertEqual(live.pixels[16][24], (40, 110, 230))
        self.assertEqual(live.pixels[6][26], (236, 190, 69))
        self.assertEqual(final.pixels[6][26], (0, 0, 0))
        self.assertEqual(live.pixels[25], final.pixels[25])
        # Sprite artwork must not touch the first score column.
        for y in list(range(6, 15)) + list(range(16, 25)):
            self.assertEqual(live.pixels[y][35:40], final.pixels[y][35:40])

    def test_playoff_sprite_aliases_and_score_clearance(self):
        for away, home in (('ATL', 'CLE'), ('CLE', 'TBR'), ('TBR', 'LAD')):
            with self.subTest(away=away, home=home):
                game = BaseballGame(away=away, home=home)
                live = MLBPaletteScreen(game).render()
                final = MLBPaletteScreen(BaseballGame(away=away, home=home, status='final')).render()
                self.assertTrue(any(live.pixels[y][x] != final.pixels[y][x]
                                    for y in range(6, 25) for x in range(24, 35)))
                for y in list(range(6, 15)) + list(range(16, 25)):
                    self.assertEqual(live.pixels[y][35:40], final.pixels[y][35:40])

    def test_tampa_bay_short_alias_uses_same_sprite(self):
        short = Framebuffer()
        standard = Framebuffer()
        self.assertTrue(draw_team_mark(short, 'TB', 24, 6))
        self.assertTrue(draw_team_mark(standard, 'TBR', 24, 6))
        self.assertEqual(short.pixels, standard.pixels)

    def test_marks_only_on_live_classic(self):
        live = MLBPaletteScreen(BaseballGame(away='PHI', home='ATL')).render()
        final = MLBPaletteScreen(BaseballGame(away='PHI', home='ATL', status='final')).render()
        self.assertNotEqual(live.pixels[7][25], (0, 0, 0))
        self.assertEqual(final.pixels[7][25], (0, 0, 0))
        self.assertEqual(live.pixels[25][25], live.pixels[25][0])

if __name__ == '__main__':
    unittest.main()
