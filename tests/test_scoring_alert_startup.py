"""Guard the actual application wiring, not just isolated alert adapters."""
import inspect
import unittest

from universal_led import configurator


class ScoringAlertStartupTests(unittest.TestCase):
    def test_shared_disabled_queue_is_wired_to_every_soccer_renderer_and_board(self):
        source = inspect.getsource(configurator.main)
        self.assertIn("scoring_alerts = ScoringAlerts()", source)
        self.assertIn("ConfiguredSoccerRenderer(soccer_feed, league=league, scoring_alerts=scoring_alerts)", source)
        self.assertIn("EnglishFootballRenderer(english_feeds, scoring_alerts=scoring_alerts)", source)
        self.assertIn("english_renderer=english_renderer, scoring_alerts=scoring_alerts, standings_rotation=standings_rotation)", source)


if __name__ == "__main__":
    unittest.main()
