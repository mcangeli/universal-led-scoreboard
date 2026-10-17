import unittest

from universal_led.colors import readable_on_black
from universal_led.nhl_data import HockeyGame
from universal_led.nhl_visual import NHLVisualScreen


def sample_game():
    return HockeyGame(
        game_id=1, start_utc=None, away="BOS", home="NYR",
        away_name="Boston", home_name="New York",
        away_score=1, home_score=0, status="live",
    )


class NHLVisualContrastTests(unittest.TestCase):
    def test_dark_team_color_is_readable(self):
        colors = {"BOS": (0, 0, 35)}
        game = sample_game()
        frame = NHLVisualScreen(game=game, team_colors=colors).render()
        expected = readable_on_black(colors["BOS"])
        self.assertIn(expected, [pixel for row in frame.pixels[10:16] for pixel in row])

    def test_original_team_colors_unchanged(self):
        colors = {"BOS": (0, 0, 35)}
        NHLVisualScreen(game=HockeyGame(away="BOS", home="NYR"), team_colors=colors).render()
        self.assertEqual(colors["BOS"], (0, 0, 35))


if __name__ == "__main__":
    unittest.main()
