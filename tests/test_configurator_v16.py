import unittest
from universal_led.configurator import HTML,make_handler
from universal_led.sport_settings import DEFAULT_SETTINGS

class Preview16Tests(unittest.TestCase):
    def test_navigation_and_status(self):
        for text in ("showPage('display')","save-settings","saveClockSettings()","/api/status","current-game","system-info","refreshStatus"):
            with self.subTest(text=text):
                self.assertIn(text,HTML)
    def test_sport_inputs_are_on_sports_page(self):
        sports = HTML.split('<section data-page="sports"', 1)[1].split('<section data-page="display"', 1)[0]
        for control in ('id="rotation"','id="refresh"','id="mode"', 'id="mlb-enabled"', 'id="nhl-enabled"'):
            self.assertIn(control,sports)

    def test_shared_display_controls(self):
        display = HTML.split('<section data-page="display"', 1)[1].split('<section data-page="wifi"', 1)[0]
        for control in ('id="clock-enabled"', 'id="weather-enabled"', 'id="countdown-enabled"'):
            self.assertIn(control,display)
    def test_existing_editor_preserved(self):
        for control in ('id="matrix"','id="save"','id="cancel"','id="reset"'):
            self.assertIn(control,HTML)
    def test_handler_construction(self):
        self.assertTrue(make_handler('/tmp','test-token'))
    def test_default_rotation(self):
        self.assertGreater(DEFAULT_SETTINGS['mlb']['rotation_seconds'],0)
if __name__=='__main__':
    unittest.main()
