"""English game coverage and standings page selection are independent."""
import copy
import inspect
import unittest
from universal_led import configurator
from universal_led.sport_settings import DEFAULT_SETTINGS, validate_settings


class EnglishStandingsPreferencesTests(unittest.TestCase):
    def test_selection_can_differ_from_enabled_game_leagues(self):
        settings = copy.deepcopy(DEFAULT_SETTINGS)
        settings['english']['enabled_leagues'] = ['EPL', 'CHAMPIONSHIP']
        settings['standings']['leagues'] = ['CHAMPIONSHIP']
        validated = validate_settings(settings)
        self.assertEqual(validated['standings']['leagues'], ['CHAMPIONSHIP'])
        self.assertEqual(validated['english']['enabled_leagues'], ['EPL', 'CHAMPIONSHIP'])

    def test_empty_selection_is_allowed(self):
        settings = copy.deepcopy(DEFAULT_SETTINGS)
        settings['standings']['leagues'] = []
        self.assertEqual(validate_settings(settings)['standings']['leagues'], [])

    def test_unknown_and_duplicate_leagues_are_rejected(self):
        for leagues in (['NOT_A_LEAGUE'], ['EPL', 'EPL'], 'EPL'):
            with self.subTest(leagues=leagues):
                settings = copy.deepcopy(DEFAULT_SETTINGS)
                settings['standings']['leagues'] = leagues
                with self.assertRaises(ValueError):
                    validate_settings(settings)

    def test_dashboard_and_startup_wire_selections(self):
        self.assertIn('id="english-standings-leagues"', configurator.HTML)
        self.assertIn("next.standings.leagues=Array.from(", configurator.HTML)
        source = inspect.getsource(configurator.main)
        self.assertIn("selected_standings_leagues = standings_options.get('leagues', english['enabled_leagues'])", source)
        self.assertIn("selected_mlb_divisions = standings_options.get('mlb_divisions', [])", source)
        self.assertIn("selected_nhl_divisions = standings_options.get('nhl_divisions', [])", source)
        self.assertIn("selected_leagues=[*selected_standings_leagues, *selected_mlb_groups,", source)
        self.assertIn("*selected_nhl_groups])", source)
        self.assertIn("if needs_pregame_records or needs_standings_page:", source)


if __name__ == '__main__':
    unittest.main()
