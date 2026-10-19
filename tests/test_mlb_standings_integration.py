"""MLB standings controls and cache wiring regression checks."""
import copy
import inspect
import unittest

from universal_led import configurator
from universal_led.sport_settings import DEFAULT_SETTINGS, validate_settings


class MLBStandingsIntegrationTests(unittest.TestCase):
    def test_six_division_controls_in_mlb_setup(self):
        html = configurator.HTML
        self.assertIn('id="mlb-standings-divisions"', html)
        for key in ('AL_EAST', 'AL_CENTRAL', 'AL_WEST',
                    'NL_EAST', 'NL_CENTRAL', 'NL_WEST'):
            self.assertIn('value="' + key + '"', html)

    def test_divisions_validate_without_changing_game_settings(self):
        settings = copy.deepcopy(DEFAULT_SETTINGS)
        settings['sports']['mlb']['enabled'] = True
        settings['standings']['mlb_divisions'] = ['NL_EAST']
        result = validate_settings(settings)
        self.assertEqual(result['standings']['mlb_divisions'], ['NL_EAST'])
        self.assertTrue(result['sports']['mlb']['enabled'])

    def test_invalid_divisions_rejected(self):
        for selection in ('NL_EAST', ['NL_EAST', 'NL_EAST'], ['UNKNOWN']):
            with self.subTest(selection=selection):
                settings = copy.deepcopy(DEFAULT_SETTINGS)
                settings['standings']['mlb_divisions'] = selection
                with self.assertRaises(ValueError):
                    validate_settings(settings)

    def test_runtime_wires_mlb_standings_independently(self):
        source = inspect.getsource(configurator.main)
        self.assertIn('mlb_standings_workers', source)
        self.assertIn('selected_mlb_divisions', source)
        self.assertIn('standings_caches.update(mlb_standings_caches)', source)


if __name__ == '__main__':
    unittest.main()
