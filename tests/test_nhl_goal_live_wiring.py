"""NHL feed callback is wired to the dedicated goal observer."""
import unittest
from pathlib import Path
from universal_led.nhl_engine import ConfiguredNHLRenderer
from universal_led.score_change_observer import NHLGoalObserver


class NHLGoalIntegrationTests(unittest.TestCase):
    def test_nhl_renderer_uses_goal_observer(self):
        class Feed:
            pass
        renderer=ConfiguredNHLRenderer(Feed())
        self.assertIsInstance(renderer.score_observer,NHLGoalObserver)

    def test_configurator_observes_nhl_on_background_refresh(self):
        from universal_led import configurator
        source=Path(configurator.__file__).read_text(encoding='utf-8')
        self.assertIn('nhl_feed.on_games = lambda games:',source)
        self.assertIn('nhl_renderer.score_observer.observe(games, favorite_teams=nhl_renderer.favorite_teams)',source)
        self.assertIn("observe_finals('nhl', games)",source)


if __name__=='__main__':
    unittest.main()
