"""English soccer integration regressions, independent of network."""
import unittest
from datetime import date
from unittest.mock import patch

from universal_led.soccer import SUPPORTED_LEAGUES, SoccerMatch, GoalEventTracker
from universal_led.soccer_data import SoccerFeed, fetch_scores
from universal_led.soccer_engine import ConfiguredSoccerRenderer


def payload():
    return {"events": [{"id": "game1", "status": {"type": {"state": "pre"}},
                        "competitions": [{"competitors": [
                            {"homeAway": "home", "team": {"abbreviation": "CFC"}, "score": "0"},
                            {"homeAway": "away", "team": {"abbreviation": "MUN"}, "score": "0"}]}]}]}


class EnglishFeedIntegrationTests(unittest.TestCase):
    def test_all_four_leagues_enabled(self):
        self.assertTrue({"EPL", "CHAMPIONSHIP", "LEAGUE_ONE", "LEAGUE_TWO"} <= SUPPORTED_LEAGUES)

    def test_existing_soccer_still_supported(self):
        self.assertTrue({"MLS", "NWSL"} <= SUPPORTED_LEAGUES)

    def test_english_fetch_urls(self):
        class Response:
            def __enter__(self): return self
            def __exit__(self, *args): pass
            def read(self): return b'{"events":[]}'
        for league, slug in (("EPL", "eng.1"), ("CHAMPIONSHIP", "eng.2"),
                             ("LEAGUE_ONE", "eng.3"), ("LEAGUE_TWO", "eng.4")):
            with self.subTest(league=league):
                with patch("universal_led.soccer_data.urlopen", return_value=Response()) as mock:
                    fetch_scores(league, date(2026, 10, 17))
                    self.assertIn(f"/{slug}/scoreboard?dates=20261017", mock.call_args.args[0].full_url)

    def test_english_feed_normalizes(self):
        for league in ("EPL", "CHAMPIONSHIP", "LEAGUE_ONE", "LEAGUE_TWO"):
            with self.subTest(league=league):
                feed = SoccerFeed(league, fetcher=lambda *args: payload())
                game = feed.refresh(date(2026, 10, 17))[0]
                self.assertEqual((game.league, game.home_id, game.away_id), (league, "CFC", "MUN"))
                renderer = ConfiguredSoccerRenderer(feed, league=league)
                self.assertTrue(renderer.has_games())

    def test_goal_tracker_accepts_english_leagues(self):
        tracker = GoalEventTracker()
        self.assertEqual(tracker.observe(SoccerMatch("g1", "EPL", "CFC", "MUN", 0, 0, "pre")), ())

    def test_english_league_isolation(self):
        feed = SoccerFeed("EPL", fetcher=lambda *args: payload())
        feed.refresh(date(2026, 10, 17))
        renderer = ConfiguredSoccerRenderer(feed, league="CHAMPIONSHIP")
        self.assertFalse(renderer.has_games())


if __name__ == "__main__":
    unittest.main()
