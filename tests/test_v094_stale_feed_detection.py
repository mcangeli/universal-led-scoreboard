"""Detect cached sports feeds that silently stop refreshing."""
import unittest
from datetime import date
from unittest.mock import patch

from universal_led.nba_feed import NBAFeed
from universal_led.nhl_feed import NHLFeed


class StaleFeedDetectionTests(unittest.TestCase):
    def check_staleness(self, feed_type, parser):
        now = [100.0]
        feed = feed_type(fetcher=lambda day: {}, refresh_seconds=60,
                         clock=lambda: now[0])
        with patch(parser, return_value=[]):
            self.assertEqual(feed.status()["state"], "starting")
            feed.refresh(date(2026, 11, 21))
            self.assertEqual(feed.status()["state"], "running")
            now[0] += 180
            self.assertEqual(feed.status()["state"], "running")
            now[0] += 1
            self.assertEqual(feed.status()["state"], "stale")
            feed.refresh(date(2026, 11, 21))
            self.assertEqual(feed.status()["state"], "running")

    def test_nba_stale_and_recovers(self):
        self.check_staleness(NBAFeed, "universal_led.nba_feed.parse_scoreboard")

    def test_nhl_stale_and_recovers(self):
        self.check_staleness(NHLFeed, "universal_led.nhl_feed.parse_scoreboard")

    def test_nba_failed_refresh_is_error_not_stale(self):
        self.check_failure(NBAFeed, "universal_led.nba_feed.parse_scoreboard")

    def test_nhl_failed_refresh_is_error_not_stale(self):
        self.check_failure(NHLFeed, "universal_led.nhl_feed.parse_scoreboard")

    def check_failure(self, feed_type, parser):
        now = [100.0]
        offline = [False]
        def fetch(day):
            if offline[0]:
                raise TimeoutError("offline")
            return {}
        feed = feed_type(fetcher=fetch, clock=lambda: now[0])
        with patch(parser, return_value=[]):
            feed.refresh(date(2026, 11, 21))
            offline[0] = True
            now[0] += 200
            feed.refresh(date(2026, 11, 21))
            self.assertEqual(feed.status()["state"], "error")


if __name__ == "__main__":
    unittest.main()
