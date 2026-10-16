import tempfile
import unittest
from unittest.mock import patch

from universal_led.config_store import save_config
from universal_led.nhl_engine import ConfiguredNHLRenderer


class DummyFeed:
    def games(self):
        return []


class NHLRendererColorsTests(unittest.TestCase):
    def test_renderer_receives_persisted_palette_and_live_updates(self):
        with tempfile.TemporaryDirectory() as directory:
            renderer = ConfiguredNHLRenderer(DummyFeed(), config_dir=directory)
            with patch('universal_led.nhl_engine.NHLVisualScreen') as screen:
                renderer.frame()
                self.assertNotEqual(screen.call_args.kwargs['team_colors']['BOS'], (1, 2, 3))
                save_config(directory, 'nhl_teams', {'BOS': [1, 2, 3]})
                renderer.frame()
                self.assertEqual(screen.call_args.kwargs['team_colors']['BOS'], (1, 2, 3))
                screen.return_value.render.assert_called()

    def test_legacy_renderer_without_config_dir(self):
        renderer = ConfiguredNHLRenderer(DummyFeed())
        with patch('universal_led.nhl_engine.NHLVisualScreen') as screen:
            renderer.frame()
            self.assertIsNone(screen.call_args.kwargs['team_colors'])


if __name__ == '__main__':
    unittest.main()
