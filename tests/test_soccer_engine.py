import unittest

from universal_led.soccer import SoccerGoal, SoccerMatch
from universal_led.soccer_engine import ConfiguredSoccerRenderer


class Feed:
    def __init__(self, games):
        self._games = games

    def games(self):
        return self._games


def match(league="MLS", status="in", home="ATL", goals=()):
    return SoccerMatch(home, league, home, "MIA", 2, 1, status, tuple(goals))


class SoccerEngineTests(unittest.TestCase):
    def test_no_games_renders_blank_frame(self):
        renderer = ConfiguredSoccerRenderer(Feed([]), league="MLS")
        self.assertEqual((renderer.frame().width, renderer.frame().height), (64, 32))
        self.assertFalse(renderer.has_games())

    def test_live_match_is_detected(self):
        renderer = ConfiguredSoccerRenderer(Feed([match()]), league="MLS")
        self.assertTrue(renderer.has_live_games())

    def test_live_detection_accepts_whitespace_and_case(self):
        renderer = ConfiguredSoccerRenderer(Feed([match(status=" LIVE ")]), league="MLS")
        self.assertTrue(renderer.has_live_games())

    def test_live_detection_accepts_in_progress(self):
        renderer = ConfiguredSoccerRenderer(Feed([match(status="IN_PROGRESS")]), league="MLS")
        self.assertTrue(renderer.has_live_games())

    def test_scheduled_match_is_not_live(self):
        renderer = ConfiguredSoccerRenderer(Feed([match(status="pre")]), league="MLS")
        self.assertFalse(renderer.has_live_games())

    def test_league_filter_is_independent(self):
        renderer = ConfiguredSoccerRenderer(Feed([match("NWSL")]), league="MLS")
        self.assertFalse(renderer.has_games())

    def test_favorites_only_filters(self):
        renderer = ConfiguredSoccerRenderer(Feed([match()]), league="MLS", mode="favorite", favorite_teams=["NY"])
        self.assertIsNone(renderer.game())

    def test_live_preferred_over_scheduled(self):
        games = [match(status="pre"), match(home="NY")]
        renderer = ConfiguredSoccerRenderer(Feed(games), league="MLS")
        self.assertEqual(renderer.game().home_id, "NY")

    def test_goal_update_produces_goal_frame(self):
        now = [10.]
        feed = Feed([match()])
        renderer = ConfiguredSoccerRenderer(feed, league="MLS", clock=lambda: now[0])
        renderer.update(feed.games()[0])
        updated = match(goals=[SoccerGoal("g1", "ATL", "Scorer", "67")])
        feed._games = [updated]
        renderer.update(updated)
        self.assertEqual(renderer.display.screen(updated, now[0]).kind, "goal")
        self.assertEqual(renderer.frame().width, 64)

    def test_wrong_league_update_is_ignored(self):
        renderer = ConfiguredSoccerRenderer(Feed([]), league="MLS")
        renderer.update(match("NWSL"))
        self.assertEqual(renderer.display._latest, {})

    def test_invalid_mode_rejected(self):
        with self.assertRaises(ValueError):
            ConfiguredSoccerRenderer(Feed([]), league="MLS", mode="unknown")


if __name__ == "__main__":
    unittest.main()
