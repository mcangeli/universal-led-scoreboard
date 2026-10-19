"""Standings workers run independently from game coverage."""
import inspect
import unittest
from universal_led import configurator


class IndependentStandingsWorkersTests(unittest.TestCase):
    def test_standings_enabled_independent_of_english_game_toggle(self):
        source = inspect.getsource(configurator.main)
        self.assertIn("enabled=standings_options['enabled']", source)
        self.assertIn("needs_standings_page = (standings_options['enabled'] and", source)
        self.assertIn("league in selected_standings_leagues", source)

    def test_pregame_records_keep_background_feed(self):
        source = inspect.getsource(configurator.main)
        self.assertIn("needs_pregame_records = (settings['sports']['english']['enabled'] and", source)
        self.assertIn("if needs_pregame_records or needs_standings_page:", source)


if __name__ == "__main__":
    unittest.main()
