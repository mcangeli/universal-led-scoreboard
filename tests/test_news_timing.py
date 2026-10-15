import copy
import tempfile
import unittest
from universal_led.sport_settings import DEFAULT_SETTINGS, load_settings, save_settings, validate_settings
from universal_led.configurator import HTML


class NewsTimingTests(unittest.TestCase):
    def test_default_timing(self):
        self.assertEqual(DEFAULT_SETTINGS['news']['rotation_interval'],5)
        self.assertEqual(DEFAULT_SETTINGS['news']['headline_seconds'],12)

    def test_legacy_settings_are_upgraded(self):
        settings=copy.deepcopy(DEFAULT_SETTINGS)
        settings.pop('news')
        self.assertEqual(validate_settings(settings)['news'],DEFAULT_SETTINGS['news'])

    def test_invalid_timing_rejected(self):
        for key,bad in [('rotation_interval',0),('headline_seconds',121),('scroll_chars_per_second',True)]:
            settings=copy.deepcopy(DEFAULT_SETTINGS)
            settings['news'][key]=bad
            with self.subTest(key=key),self.assertRaises(ValueError):
                validate_settings(settings)

    def test_timing_persists(self):
        with tempfile.TemporaryDirectory() as directory:
            settings=copy.deepcopy(DEFAULT_SETTINGS)
            settings['news']['rotation_interval']=3
            save_settings(directory,settings)
            self.assertEqual(load_settings(directory)['news']['rotation_interval'],3)

    def test_timing_editor(self):
        self.assertIn('id="news-interval"',HTML)
        self.assertIn('id="news-duration"',HTML)
        self.assertIn('id="news-speed"',HTML)


if __name__=='__main__':
    unittest.main()
