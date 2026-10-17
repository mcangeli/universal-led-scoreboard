import unittest
from datetime import date
from unittest.mock import patch

from universal_led.soccer_data import SoccerFeed, fetch_scores
from universal_led.soccer_runtime import BackgroundSoccerFeed


def payload():
    return {"events": [{"id": "g1", "status": {"type": {"state": "in"}},
                        "competitions": [{"competitors": [
                            {"homeAway": "home", "team": {"abbreviation": "ATL"}, "score": "1"},
                            {"homeAway": "away", "team": {"abbreviation": "MIA"}, "score": "0"}]}]}]}


class SoccerDataTests(unittest.TestCase):
    def setUp(self):
        self.day = date(2026, 10, 17)

    def test_mls_fetch_url(self):
        class Response:
            def __enter__(self):
                return self
            def __exit__(self, *args):
                pass
            def read(self):
                return b'{"events": []}'
        with patch("universal_led.soccer_data.urlopen", return_value=Response()) as mock:
            self.assertEqual(fetch_scores("MLS", self.day), {"events": []})
            self.assertIn("/usa.1/scoreboard?dates=20261017", mock.call_args.args[0].full_url)

    def test_nwsl_fetch_url(self):
        class Response:
            def __enter__(self):
                return self
            def __exit__(self, *args):
                pass
            def read(self):
                return b'{"events": []}'
        with patch("universal_led.soccer_data.urlopen", return_value=Response()) as mock:
            fetch_scores("NWSL", self.day)
            self.assertIn("/usa.nwsl/scoreboard", mock.call_args.args[0].full_url)

    def test_feed_normalizes_matches(self):
        feed = SoccerFeed("MLS", fetcher=lambda league, day: payload())
        self.assertEqual(feed.refresh(self.day)[0].home_id, "ATL")

    def test_refresh_throttled(self):
        calls = []
        def fetcher(league, day):
            calls.append(day)
            return payload()
        feed = SoccerFeed("MLS", fetcher=fetcher, clock=lambda: 0)
        feed.refresh(self.day)
        feed.refresh(self.day)
        self.assertEqual(len(calls), 1)

    def test_failed_refresh_keeps_last_good_games(self):
        state = [False]
        def fetcher(league, day):
            if state[0]:
                raise OSError("offline")
            return payload()
        feed = SoccerFeed("MLS", fetcher=fetcher)
        feed.refresh(self.day)
        state[0] = True
        self.assertEqual(len(feed.refresh(self.day, force=True)), 1)
        self.assertEqual(feed.status()["state"], "error")

    def test_league_rejected(self):
        with self.assertRaises(ValueError):
            SoccerFeed("EFL")

    def test_invalid_refresh_interval(self):
        with self.assertRaises(ValueError):
            SoccerFeed("MLS", refresh_seconds=0)

    def test_background_callback_receives_matches(self):
        feed = SoccerFeed("MLS", fetcher=lambda league, day: payload())
        seen = []
        worker = BackgroundSoccerFeed(feed, day_provider=lambda: self.day, on_match=seen.append)
        worker.refresh_once()
        self.assertEqual(len(seen), 1)

    def test_background_failure_does_not_forward_stale_goals(self):
        state = [False]
        def fetcher(league, day):
            if state[0]:
                raise OSError("offline")
            return payload()
        feed = SoccerFeed("MLS", fetcher=fetcher)
        seen = []
        worker = BackgroundSoccerFeed(feed, day_provider=lambda: self.day, on_match=seen.append)
        worker.refresh_once()
        state[0] = True
        feed.refresh(self.day, force=True)
        worker.refresh_once()
        self.assertEqual(len(seen), 1)


if __name__ == "__main__":
    unittest.main()
