import unittest
from universal_led.configurator import HTML
from universal_led.season_countdown_settings import DEFAULT, validate

class CountdownConfiguratorTests(unittest.TestCase):
    def test_fields_and_actions_present(self):
        for field in ('enabled','sport','season','opening','target','team','window','days','status'):
            self.assertEqual(HTML.count('id="countdown-'+field+'"'),1)
        self.assertIn('async function loadCountdown()',HTML)
        self.assertIn('async function saveCountdown()',HTML)
        self.assertIn('/api/season-countdown',HTML)

    def test_disabled_defaults(self):
        self.assertFalse(validate(DEFAULT)['enabled'])

    def test_enabled_requires_date(self):
        with self.assertRaises(ValueError):
            validate(dict(DEFAULT, enabled=True))

    def test_valid_manual_date(self):
        settings=dict(DEFAULT,enabled=True,season='2027',opening_at='2027-03-25T13:00:00-04:00')
        self.assertEqual(validate(settings)['opening_at'],settings['opening_at'])

if __name__ == '__main__':
    unittest.main()
