import unittest
from unittest.mock import patch

from universal_led.colors import readable_on_black
from universal_led.mlb_classic import BaseballGame
from universal_led.mlb_visual import MLBVisualScreen, TEAM_COLORS


class MLBVisualContrastTests(unittest.TestCase):
    def test_dark_team_accent_is_brightened_in_frame(self):
        with patch.dict(TEAM_COLORS, {"ATL": (0, 0, 40)}):
            frame = MLBVisualScreen(BaseballGame(away="ATL", home="MIA")).render()
        expected = readable_on_black((0, 0, 40))
        self.assertIn(expected, [pixel for row in frame.pixels[7:14] for pixel in row])

    def test_team_palette_not_mutated_by_render(self):
        original = TEAM_COLORS["ATL"]
        MLBVisualScreen(BaseballGame(away="ATL", home="MIA")).render()
        self.assertEqual(TEAM_COLORS["ATL"], original)


if __name__ == "__main__":
    unittest.main()
