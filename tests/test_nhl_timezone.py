"""NHL scheduled times follow the shared clock preferences."""
import unittest
from universal_led.nhl_data import parse_game
from universal_led.nhl_screen import status_text


class NHLTimezoneTests(unittest.TestCase):
    def setUp(self):
        self.game = parse_game({
            "id": 1, "gameState": "FUT", "startTimeUTC": "2026-10-16T23:00:00Z",
            "awayTeam": {"abbrev": "BOS"}, "homeTeam": {"abbrev": "NYR"},
        })

    def test_eastern_daylight_time(self):
        self.assertEqual(status_text(self.game, "America/New_York", "12h"), "7:00PM EDT")

    def test_pacific_daylight_time(self):
        self.assertEqual(status_text(self.game, "America/Los_Angeles", "12h"), "4:00PM PDT")

    def test_twenty_four_hour_format(self):
        self.assertEqual(status_text(self.game, "America/New_York", "24h"), "19:00 EDT")

    def test_utc_can_still_be_selected(self):
        self.assertEqual(status_text(self.game, "UTC", "24h"), "23:00 UTC")


if __name__ == "__main__":
    unittest.main()
