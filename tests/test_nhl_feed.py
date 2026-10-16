"""Offline NHL feed transport/cache regression tests."""
import unittest
from datetime import date
from unittest.mock import patch

from universal_led.nhl_feed import NHLFeed, fetch_scores


DAY = date(2026, 10, 16)


def payload(score=2):
    return {"games": [{
        "id": 2026020001, "gameState": "LIVE",
        "awayTeam": {"abbrev": "BOS", "score": score},
        "homeTeam": {"abbrev": "NYR", "score": 1},
    }]}


class NHLFeedTests(unittest.TestCase):
    def test_initial_and_cached_refresh(self):
        calls = []
        now = [100.0]
        def fetch(day):
            calls.append(day)
            return payload()
        feed = NHLFeed(fetcher=fetch, clock=lambda: now[0])
        self.assertEqual(feed.refresh(DAY)[0].away_score, 2)
        self.assertEqual(feed.refresh(DAY)[0].away_score, 2)
        self.assertEqual(calls, [DAY])
        self.assertEqual(feed.status()["state"], "running")

    def test_expiry_and_force(self):
        calls = []
        now = [100.0]
        def fetch(day):
            calls.append(day)
            return payload(len(calls))
        feed = NHLFeed(fetcher=fetch, clock=lambda: now[0])
        feed.refresh(DAY)
        now[0] = 161.0
        self.assertEqual(feed.refresh(DAY)[0].away_score, 2)
        self.assertEqual(feed.refresh(DAY, force=True)[0].away_score, 3)

    def test_failure_preserves_last_good_games(self):
        calls = [0]
        def fetch(day):
            calls[0] += 1
            if calls[0] > 1:
                raise OSError("offline")
            return payload()
        feed = NHLFeed(fetcher=fetch)
        feed.refresh(DAY)
        self.assertEqual(feed.refresh(DAY, force=True)[0].away_score, 2)
        self.assertEqual(feed.status()["state"], "error")
        self.assertIn("offline", feed.status()["error"])
        self.assertIsNotNone(feed.status()["last_success"])

    def test_bad_payload_does_not_overwrite_cache(self):
        responses = iter([payload(), {"games": "bad"}])
        feed = NHLFeed(fetcher=lambda day: next(responses))
        feed.refresh(DAY)
        self.assertEqual(len(feed.refresh(DAY, force=True)), 1)
        self.assertEqual(feed.status()["state"], "error")

    def test_new_day_fetches_even_before_expiry(self):
        calls = []
        feed = NHLFeed(fetcher=lambda day: calls.append(day) or {"games": []})
        feed.refresh(DAY)
        feed.refresh(date(2026, 10, 17))
        self.assertEqual(len(calls), 2)

    def test_invalid_refresh_interval(self):
        with self.assertRaises(ValueError):
            NHLFeed(refresh_seconds=0)

    def test_transport_url_and_timeout(self):
        class Response:
            def __enter__(self):
                return self
            def __exit__(self, *args):
                pass
            def read(self, *args):
                return b'{"games":[]}'
        with patch("universal_led.nhl_feed.urlopen", return_value=Response()) as url:
            self.assertEqual(fetch_scores(DAY), {"games": []})
            url.assert_called_once_with(
                "https://api-web.nhle.com/v1/score/2026-10-16", timeout=5.0)

    def test_transport_rejects_invalid_timeout(self):
        with self.assertRaises(ValueError):
            fetch_scores(DAY, timeout=0)


if __name__ == "__main__":
    unittest.main()
