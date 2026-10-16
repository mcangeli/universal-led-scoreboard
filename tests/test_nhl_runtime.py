import unittest
from datetime import date
from universal_led.nhl_feed import NHLFeed
from universal_led.nhl_runtime import BackgroundNHLFeed, select_games
from universal_led.nhl_data import parse_game


def game(away, home):
    return parse_game({"id": 1, "gameState": "FUT",
                       "awayTeam": {"abbrev": away},
                       "homeTeam": {"abbrev": home}})


class NHLRuntimeTests(unittest.TestCase):
    def test_favorite_selection(self):
        games = [game("BOS", "NYR"), game("TOR", "MTL")]
        self.assertEqual(select_games(games, "BOS", "favorite"), games[:1])

    def test_fallback_when_favorite_not_playing(self):
        games = [game("BOS", "NYR")]
        self.assertEqual(select_games(games, "SEA", "fallback"), games)

    def test_favorite_absent_returns_empty(self):
        self.assertEqual(select_games([game("BOS", "NYR")], "SEA", "favorite"), [])

    def test_all_mode_and_multiple_favorites(self):
        games = [game("BOS", "NYR"), game("TOR", "MTL")]
        self.assertEqual(select_games(games, "SEA", "all"), games)
        self.assertEqual(select_games(games, ["NYR", "MTL"]), games)

    def test_bad_mode(self):
        with self.assertRaises(ValueError):
            select_games([], mode="invalid")

    def test_background_wrapper_refresh(self):
        calls = []
        feed = NHLFeed(fetcher=lambda day: calls.append(day) or {"games": []})
        worker = BackgroundNHLFeed(feed, day_provider=lambda: date(2026, 10, 16))
        worker.refresh_once()
        self.assertEqual(calls, [date(2026, 10, 16)])
        self.assertEqual(worker.games(), [])
        self.assertEqual(worker.status()["state"], "running")

    def test_start_and_stop(self):
        import threading
        triggered = threading.Event()
        feed = NHLFeed(fetcher=lambda day: triggered.set() or {"games": []})
        worker = BackgroundNHLFeed(feed, day_provider=lambda: date(2026, 10, 16))
        worker.start()
        self.assertTrue(triggered.wait(2))
        worker.stop()
        self.assertIsNone(worker._thread)


if __name__ == "__main__":
    unittest.main()
