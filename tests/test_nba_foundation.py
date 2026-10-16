"""Offline NBA foundation regression tests."""
import unittest
from datetime import date
from universal_led.nba_data import parse_scoreboard
from universal_led.nba_feed import NBAFeed
from universal_led.nba_runtime import BackgroundNBAFeed, select_games

DAY = date(2026, 10, 16)

def payload(state="STATUS_IN_PROGRESS"):
    return {"events": [{"id": "401", "date": "2026-10-17T00:00:00Z",
        "status": {"type": {"name": state, "shortDetail": "Q3"}, "period": 3, "displayClock": "4:32"},
        "competitions": [{"competitors": [
            {"homeAway": "away", "team": {"abbreviation": "ATL", "displayName": "Atlanta Hawks"}, "score": "101"},
            {"homeAway": "home", "team": {"abbreviation": "BOS", "displayName": "Boston Celtics"}, "score": "99"}]}]}]}

class NBAFoundationTests(unittest.TestCase):
    def test_live_game(self):
        game = parse_scoreboard(payload())[0]
        self.assertEqual((game.away, game.home, game.away_score, game.home_score), ("ATL", "BOS", 101, 99))
        self.assertEqual((game.status, game.period, game.clock), ("live", 3, "4:32"))

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
        feed = NBAFeed(fetcher=fetch)
        self.assertEqual(len(feed.refresh(DAY)), 1)
        self.assertEqual(len(feed.refresh(DAY, force=True)), 1)
        self.assertEqual(feed.status()["state"], "error")
        self.assertEqual(feed.refresh(DAY, force=True), [])
        self.assertEqual(feed.status()["state"], "running")

    def test_team_selection(self):
        games = parse_scoreboard(payload())
        self.assertEqual(len(select_games(games, ["ATL"], "favorite")), 1)
        self.assertEqual(select_games(games, ["NYK"], "favorite"), [])
        self.assertEqual(len(select_games(games, ["NYK"], "fallback")), 1)

    def test_worker_lifecycle(self):
        feed = NBAFeed(fetcher=lambda day: {"events": []})
        worker = BackgroundNBAFeed(feed, day_provider=lambda: DAY)
        self.assertEqual(worker.refresh_once(), [])
        worker.start()
        worker.stop()
        self.assertIsNone(worker._thread)

if __name__ == "__main__":
    unittest.main()
