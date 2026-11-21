"""Fault injection for cached NBA/NHL refresh paths without network calls."""
import unittest
from datetime import date
from unittest.mock import patch

from universal_led.nba_feed import NBAFeed
from universal_led.nhl_feed import NHLFeed


class CachedFeedRecoveryTests(unittest.TestCase):
    def test_nba_preserves_last_good_snapshot_then_recovers(self):
        self._exercise(NBAFeed, "universal_led.nba_feed.parse_scoreboard")

    def test_nhl_preserves_last_good_snapshot_then_recovers(self):
        self._exercise(NHLFeed, "universal_led.nhl_feed.parse_scoreboard")

    def _exercise(self, feed_class, parser_path):
        now = [100.0]
        state = {"fail": False, "version": 1}
        def fetcher(day):
            if state["fail"]:
                raise TimeoutError("simulated provider timeout")
            return {"version": state["version"]}
        feed = feed_class(fetcher=fetcher, clock=lambda: now[0],
                          refresh_seconds=60)
        today = date(2026, 11, 21)
        with patch(parser_path, side_effect=lambda data: [data["version"]]):
            self.assertEqual(feed.refresh(today), [1])
            self.assertEqual(feed.status()["state"], "running")
            state["fail"] = True
            now[0] += 61
            self.assertEqual(feed.refresh(today), [1])
            self.assertEqual(feed.games(), [1])
            self.assertEqual(feed.status()["state"], "error")
            self.assertIsNotNone(feed.status()["last_success"])
            state["fail"] = False
            state["version"] = 2
            now[0] += 61
            self.assertEqual(feed.refresh(today), [2])
            self.assertEqual(feed.status()["state"], "running")
            self.assertIsNone(feed.status()["error"])

    def test_nba_initial_timeout_then_recovery(self):
        self._initial_timeout(NBAFeed, "universal_led.nba_feed.parse_scoreboard")

    def test_nhl_initial_timeout_then_recovery(self):
        self._initial_timeout(NHLFeed, "universal_led.nhl_feed.parse_scoreboard")

    def _initial_timeout(self, feed_class, parser_path):
        state = {"offline": True}
        def fetcher(day):
            if state["offline"]:
                raise ConnectionError("offline")
            return {}
        feed = feed_class(fetcher=fetcher)
        today = date(2026, 11, 21)
        with patch(parser_path, return_value=[42]):
            self.assertEqual(feed.refresh(today), [])
            self.assertEqual(feed.status()["state"], "error")
            state["offline"] = False
            self.assertEqual(feed.refresh(today, force=True), [42])
            self.assertEqual(feed.status()["state"], "running")


if __name__ == "__main__":
    unittest.main()
