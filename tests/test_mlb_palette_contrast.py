import unittest

from universal_led.colors import readable_on_black
from universal_led.mlb_classic import BaseballGame
from universal_led.mlb_palette_v11 import MLBPaletteScreen


class MLBPaletteContrastTests(unittest.TestCase):
    def test_live_team_label_is_brightened(self):
        palette = {"ATL": (0, 0, 40), "NYM": (235, 235, 225)}
        frame = MLBPaletteScreen(team_colors=palette).render()
        expected = readable_on_black(palette["ATL"])
        self.assertIn(expected, frame.pixels[17])
        self.assertEqual(palette["ATL"], (0, 0, 40))

    def test_pregame_detail_team_label_is_brightened(self):
        palette = {"ATL": (0, 0, 40), "NYM": (235, 235, 225)}
        frame = MLBPaletteScreen(
            game=BaseballGame(status="pregame"),
            team_colors=palette, pregame_page=1,
        ).render()
        expected = readable_on_black(palette["ATL"])
        self.assertIn(expected, [pixel for row in frame.pixels[20:25] for pixel in row])
        self.assertEqual(palette["ATL"], (0, 0, 40))


if __name__ == "__main__":
    unittest.main()
