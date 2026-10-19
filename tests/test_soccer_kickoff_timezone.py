"""Kickoff timezone is passed through both soccer display adapters."""
import unittest
from universal_led.soccer import SoccerMatch
from universal_led.soccer_engine import ConfiguredSoccerRenderer
from universal_led.english_rotation import EnglishFootballRenderer


class Feed:
    def __init__(self, league):
        self.league = league

    def games(self):
        return (SoccerMatch("m", self.league, "ATL", "MIA", 0, 0, "pre",
                            kickoff="2026-10-24T23:30:00Z"),)


class KickoffTimezoneTests(unittest.TestCase):
    def test_mls_timezone(self):
        renderer = ConfiguredSoccerRenderer(Feed("MLS"), league="MLS",
                                            timezone="America/Los_Angeles")
        self.assertEqual(renderer.display.screen(renderer.game(), 0).footer, "4:30PM")

    def test_english_timezone(self):
        renderer = EnglishFootballRenderer({"EPL": Feed("EPL")},
                                            timezone="America/Chicago")
        self.assertEqual(renderer.display.screen(renderer.game(), 0).footer, "6:30PM")


if __name__ == "__main__":
    unittest.main()
