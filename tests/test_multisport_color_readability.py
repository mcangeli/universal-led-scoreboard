"""Regression guards for the existing bright team-label palettes."""
import unittest

from universal_led.colors import readable_on_black
from universal_led.nba_screen import TEAM as BASKETBALL_TEAM, WHITE as BASKETBALL_AWAY
from universal_led.nfl_screen import TEAM as FOOTBALL_TEAM, WHITE as FOOTBALL_AWAY
from universal_led.soccer_pixels import WHITE as SOCCER_AWAY, GREEN as SOCCER_HOME


class MultisportColorReadabilityTests(unittest.TestCase):
    def test_basketball_team_text_is_already_readable(self):
        self.assertEqual(readable_on_black(BASKETBALL_TEAM), BASKETBALL_TEAM)
        self.assertEqual(readable_on_black(BASKETBALL_AWAY), BASKETBALL_AWAY)

    def test_football_team_text_is_already_readable(self):
        self.assertEqual(readable_on_black(FOOTBALL_TEAM), FOOTBALL_TEAM)
        self.assertEqual(readable_on_black(FOOTBALL_AWAY), FOOTBALL_AWAY)

    def test_soccer_team_text_is_already_readable(self):
        self.assertEqual(readable_on_black(SOCCER_AWAY), SOCCER_AWAY)
        self.assertEqual(readable_on_black(SOCCER_HOME), SOCCER_HOME)


if __name__ == "__main__":
    unittest.main()
