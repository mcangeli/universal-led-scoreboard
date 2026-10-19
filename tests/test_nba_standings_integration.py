"""NBA standings integration regression coverage."""
import copy
import unittest

from universal_led import configurator
from universal_led.sport_settings import DEFAULT_SETTINGS, validate_settings
from universal_led.standings import Standing
from universal_led.standings_screen import render_standings


class NBAStandingsIntegrationTests(unittest.TestCase):
    def test_conference_preferences(self):
        settings = copy.deepcopy(DEFAULT_SETTINGS)
        settings['standings']['nba_conferences'] = ['Eastern', 'Western']
        self.assertEqual(validate_settings(settings)['standings']['nba_conferences'],
                         ['Eastern', 'Western'])

    def test_invalid_conference(self):
        settings = copy.deepcopy(DEFAULT_SETTINGS)
        settings['standings']['nba_conferences'] = ['Atlantic']
        with self.assertRaises(ValueError):
            validate_settings(settings)

    def test_controls_belong_to_nba_setup(self):
        html = configurator.HTML
        panel = html.split('data-sport-panel="nba"', 1)[1].split('data-sport-panel="wnba"', 1)[0]
        self.assertIn('id="nba-standings-conferences"', panel)
        self.assertIn('next.standings.nba_conferences=Array.from(', html)

    def test_basketball_frame(self):
        rows = [Standing(league='NBA', group='Eastern', team_id='ATL',
                         abbreviation='ATL', played=50, wins=30, losses=20,
                         games_back='2.5', rank=1)]
        frame = render_standings('Eastern', rows)
        self.assertEqual(frame.width, 64)
        self.assertEqual(frame.height, 32)


if __name__ == '__main__':
    unittest.main()
