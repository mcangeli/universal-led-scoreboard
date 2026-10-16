"""WNBA league isolation and shared display regression checks."""
import unittest
from unittest.mock import patch
from datetime import date
from universal_led.wnba_feed import fetch_wnba_scores, WNBAFeed
from universal_led.nba_screen import NBAScreen


class WNBAFoundationTests(unittest.TestCase):
    def test_wnba_endpoint(self):
        with patch("universal_led.nba_feed.urlopen") as opened:
            opened.return_value.__enter__.return_value.read.return_value = b'{"events":[]}'
            self.assertEqual(fetch_wnba_scores(date(2026, 7, 1)), {"events": []})
            self.assertIn("/wnba/scoreboard", opened.call_args.args[0].full_url)

    def test_wnba_feed_empty_schedule(self):
        feed = WNBAFeed(fetcher=lambda day: {"events": []})
        self.assertEqual(feed.refresh(date(2026, 7, 1)), [])

    def test_wnba_screen_dimensions(self):
        frame = NBAScreen(league="WNBA").render()
        self.assertEqual((frame.width, frame.height), (64, 32))

    def test_reject_unknown_league(self):
        with self.assertRaises(ValueError):
            NBAScreen(league="OTHER").render()


if __name__ == "__main__":
    unittest.main()
