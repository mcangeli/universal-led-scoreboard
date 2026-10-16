"""NHL release stabilization: timezone, status labels, cached recovery."""
import unittest
from datetime import date, datetime, timezone
from unittest.mock import patch

from universal_led.nhl_data import parse_game
from universal_led.nhl_feed import NHLFeed
from universal_led.nhl_runtime import BackgroundNHLFeed
from universal_led.nhl_screen import status_text


def game(state, period=None, intermission=False):
    return parse_game({
        "id": 42, "gameState": state,
        "awayTeam": {"abbrev": "BOS", "score": 2},
        "homeTeam": {"abbrev": "NYR", "score": 3},
        "periodDescriptor": {"number": 4, "periodType": period},
        "clock": {"timeRemaining": "05:23", "inIntermission": intermission},
    })


class NHLStabilizationTests(unittest.TestCase):
    def test_local_game_day_changes_across_midnight(self):
        feed = NHLFeed(fetcher=lambda day: {"games": []})
        worker = BackgroundNHLFeed(feed, timezone_name="America/New_York")
        with patch("universal_led.nhl_runtime.datetime") as mocked:
            mocked.now.return_value = datetime(2026, 10, 17, 1, 0, tzinfo=timezone.utc)
            self.assertEqual(worker._local_day(), date(2026, 10, 16))
            worker.set_timezone("Europe/London")
            self.assertEqual(worker._local_day(), date(2026, 10, 17))

    def test_invalid_timezone_rejected(self):
        worker = BackgroundNHLFeed(NHLFeed(fetcher=lambda day: {"games": []}))
        with self.assertRaises(Exception):
            worker.set_timezone("Not/A_Timezone")

    def test_hockey_statuses(self):
        self.assertEqual(status_text(game("PPD")), "PPD")
        self.assertEqual(status_text(game("FINAL", "OT")), "FINAL OT")
        self.assertEqual(status_text(game("FINAL", "SO")), "FINAL SO")
        self.assertEqual(status_text(game("LIVE", "SO")), "SO")
        self.assertEqual(status_text(game("LIVE", "OT")), "OT 05:23")
        self.assertEqual(status_text(game("LIVE", "REG", True)), "INT")

    def test_feed_keeps_last_good_snapshot_after_failure(self):
        responses = iter(({"games": [{"id": 1, "gameState": "FINAL",
            "awayTeam": {"abbrev": "BOS"}, "homeTeam": {"abbrev": "NYR"}}]},
            OSError("network offline"), {"games": []}))
        def fetch(day):
            value = next(responses)
            if isinstance(value, Exception):
                raise value
            return value
        feed = NHLFeed(fetcher=fetch)
        today = date(2026, 10, 16)
        self.assertEqual(len(feed.refresh(today, force=True)), 1)
        self.assertEqual(len(feed.refresh(today, force=True)), 1)
        self.assertEqual(feed.status()["state"], "error")
        self.assertEqual(feed.refresh(today, force=True), [])
        self.assertEqual(feed.status()["state"], "running")


if __name__ == "__main__":
    unittest.main()
