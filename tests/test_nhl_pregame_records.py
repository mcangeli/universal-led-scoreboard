"""NHL pregame record extraction is optional and must not invent standings."""
import unittest
from universal_led.nhl_data import parse_game


class NHLRecordTests(unittest.TestCase):
    def test_record_when_supplied(self):
        game = parse_game({"id": 12, "gameState": "FUT",
                           "awayTeam": {"abbrev": "ATL", "record": "4-2-1"},
                           "homeTeam": {"abbrev": "BOS", "record": {"summary": "5-1-0"}}})
        self.assertEqual((game.away_record, game.home_record), ("4-2-1", "5-1-0"))

    def test_no_record_when_missing(self):
        game = parse_game({"id": 13, "gameState": "FUT",
                           "awayTeam": {"abbrev": "ATL"},
                           "homeTeam": {"abbrev": "BOS"}})
        self.assertEqual((game.away_record, game.home_record), ("", ""))


if __name__ == "__main__":
    unittest.main()
