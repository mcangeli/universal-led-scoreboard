import unittest
from universal_led.configurator import make_handler
from universal_led.web_preview import HTML as BOARD_HTML
from universal_led.sport_settings import DEFAULT_SETTINGS
from universal_led.runtime_settings import ConfiguredMLBRenderer

class ConfiguratorV15Tests(unittest.TestCase):
    def test_board_html_fetches_shared_frame_endpoint(self):
        self.assertIn('/frame.json',BOARD_HTML)
        self.assertIn('width="64"',BOARD_HTML)
    def test_handler_supports_board_provider(self):
        handler=make_handler('/tmp','token',board_provider=lambda: None)
        self.assertTrue(handler)
    def test_runtime_settings_include_rotation(self):
        self.assertGreater(DEFAULT_SETTINGS['mlb']['rotation_seconds'],0)
if __name__=='__main__':
    unittest.main()
