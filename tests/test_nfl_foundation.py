"""Offline NFL foundation tests."""
import unittest
from datetime import date
from universal_led.nfl_data import parse_scoreboard
from universal_led.nfl_feed import NFLFeed

DAY = date(2026, 10, 18)

def payload(state="STATUS_IN_PROGRESS"):
    return {"events": [{"id": "401", "date": "2026-10-18T17:00:00Z",
        "status": {"type": {"name": state, "shortDetail": "Q3"}, "period": 3, "displayClock": "4:32"},
        "competitions": [{"situation": {"possession": "1", "down": 2, "distance": 7},
            "competitors": [
                {"id": "1", "homeAway": "away", "team": {"abbreviation": "ATL", "displayName": "Atlanta Falcons"}, "score": "17", "records": [{"type": "total", "summary": "3-2"}]},
                {"id": "2", "homeAway": "home", "team": {"abbreviation": "CHI", "displayName": "Chicago Bears"}, "score": "14", "records": [{"type": "total", "summary": "4-1"}]}]}]}]}

class NFLFoundationTests(unittest.TestCase):
    def test_live_game(self):
        game = parse_scoreboard(payload())[0]
        self.assertEqual((game.away, game.home, game.away_score, game.home_score), ("ATL", "CHI", 17, 14))
        self.assertEqual((game.status, game.period, game.clock), ("live", 3, "4:32"))
        self.assertEqual((game.possession, game.down, game.distance), ("ATL", 2, 7))

    def test_records(self):
        game = parse_scoreboard(payload("STATUS_SCHEDULED"))[0]
        self.assertEqual((game.away_record, game.home_record), ("3-2", "4-1"))
        self.assertEqual(game.status, "scheduled")

    def test_final_and_postponed(self):
        self.assertEqual(parse_scoreboard(payload("STATUS_FINAL"))[0].status, "final")
        self.assertEqual(parse_scoreboard(payload("STATUS_POSTPONED"))[0].status, "postponed")

    def test_invalid_payload(self):
        with self.assertRaises(ValueError):
            parse_scoreboard({"events": "invalid"})

    def test_cache_and_recovery(self):
        responses = iter((payload(), OSError("offline"), {"events": []}))
        def fetch(day):
            result = next(responses)
            if isinstance(result, Exception):
                raise result
            return result
        feed = NFLFeed(fetcher=fetch)
        self.assertEqual(len(feed.refresh(DAY)), 1)
        self.assertEqual(len(feed.refresh(DAY, force=True)), 1)
        self.assertEqual(feed.status()["state"], "error")
        self.assertEqual(feed.refresh(DAY, force=True), [])
        self.assertEqual(feed.status()["state"], "running")

if __name__ == "__main__":
    unittest.main()
