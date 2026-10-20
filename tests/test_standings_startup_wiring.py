"""Guard standings cache startup independently of idle standings pages."""
import inspect
import unittest
from universal_led import configurator


class StandingsStartupWiringTests(unittest.TestCase):
    def test_standings_refresh_independent_of_idle_pages(self):
        source = inspect.getsource(configurator.main)
        self.assertIn("cache_dir=Path(args.config_dir) / 'standings-cache'", source)
        self.assertIn("settings['sports']['english']['enabled'] and", source)
        self.assertIn("league in english['enabled_leagues']", source)
        self.assertNotIn("if (standings_rotation.enabled and", source)

    def test_diagnostics_callback_reaches_http_server(self):
        source = inspect.getsource(configurator.main)
        self.assertIn("return board.soccer_pregame_diagnostics()", source)
        self.assertIn("board.frame,countdown_status,standings_status,", source)
        self.assertIn("'selected_sport':board._selected()", source)
        self.assertIn("'live_sports':list(board._live_sports())", source)


if __name__ == "__main__":
    unittest.main()
