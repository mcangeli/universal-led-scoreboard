"""Guard NHL standings setup placement and independent selection wiring."""
import inspect
import unittest
from universal_led import configurator
from universal_led.sport_settings import DEFAULT_SETTINGS, validate_settings
import copy


class NHLStandingsSetupTests(unittest.TestCase):
    def test_nhl_controls_inside_nhl_panel(self):
        html = configurator.HTML
        panel = html.split('data-sport-panel="nhl"', 1)[1].split('data-sport-panel="nba"', 1)[0]
        self.assertIn('id="nhl-standings-divisions"', panel)
        self.assertIn('id="nhl-standings-wild-cards"', panel)
        news = html.split('<legend>Standings Pages</legend>', 1)[1].split('</fieldset>', 1)[0]
        self.assertNotIn('nhl-standings-wild-cards', news)

    def test_settings_are_saved_from_sport_page(self):
        html = configurator.HTML
        self.assertIn("next.standings.nhl_divisions=Array.from(", html)
        self.assertIn("next.standings.nhl_wild_cards=Array.from(", html)

    def test_wild_card_selection_can_be_empty(self):
        settings = copy.deepcopy(DEFAULT_SETTINGS)
        settings['standings']['nhl_wild_cards'] = []
        self.assertEqual(validate_settings(settings)['standings']['nhl_wild_cards'], [])

    def test_invalid_wild_card_selection_rejected(self):
        for selected in (['Invalid'], ['Eastern_Wild_Card', 'Eastern_Wild_Card'], 'Eastern_Wild_Card'):
            with self.subTest(selected=selected):
                settings = copy.deepcopy(DEFAULT_SETTINGS)
                settings['standings']['nhl_wild_cards'] = selected
                with self.assertRaises(ValueError):
                    validate_settings(settings)


if __name__ == '__main__':
    unittest.main()
