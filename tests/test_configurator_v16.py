import unittest
from universal_led.configurator import HTML,make_handler
from universal_led.sport_settings import DEFAULT_SETTINGS

class Preview16Tests(unittest.TestCase):
    def test_navigation_and_status(self):
        for text in ("showPage('display')","save-display","/api/status","current-game","system-info","refreshStatus"):
            with self.subTest(text=text):
                self.assertIn(text,HTML)
    def test_display_inputs(self):
        for control in ('id="rotation"','id="refresh"','id="mode"'):
            self.assertIn(control,HTML)
    def test_existing_editor_preserved(self):
        for control in ('id="matrix"','id="save"','id="cancel"','id="reset"'):
            self.assertIn(control,HTML)
    def test_handler_construction(self):
        self.assertTrue(make_handler('/tmp','test-token'))
    def test_default_rotation(self):
        self.assertGreater(DEFAULT_SETTINGS['mlb']['rotation_seconds'],0)
if __name__=='__main__':
    unittest.main()
