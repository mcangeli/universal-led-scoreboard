"""Pregame records are provider-derived, never fabricated."""
import unittest
from universal_led.nba_data import parse_game


class BasketballPregameTests(unittest.TestCase):
    def test_records_from_espn(self):
        event = {"id": "100", "date": "2026-10-16T23:00:00Z",
                 "status": {"type": {"name": "STATUS_SCHEDULED"}},
                 "competitions": [{"competitors": [
                     {"homeAway": "away", "team": {"abbreviation": "ATL"}, "records": [{"type": "total", "summary": "2-1"}]},
                     {"homeAway": "home", "team": {"abbreviation": "BOS"}, "records": [{"type": "total", "summary": "3-0"}]}]}]}
        game = parse_game(event)
        self.assertEqual((game.away_record, game.home_record), ("2-1", "3-0"))

    def test_missing_records_stay_unknown(self):
        event = {"id": "101", "competitions": [{"competitors": [
            {"homeAway": "away", "team": {"abbreviation": "ATL"}},
            {"homeAway": "home", "team": {"abbreviation": "BOS"}}]}]}
        game = parse_game(event)
        self.assertEqual((game.away_record, game.home_record), ("", ""))


if __name__ == "__main__":
    unittest.main()
