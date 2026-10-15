import copy
import tempfile
import unittest
from datetime import datetime, timezone

from universal_led.clock_screen import ClockScreen
from universal_led.time_weather_settings import (
    DEFAULT_TIME_WEATHER, load_time_weather, save_time_weather,
    validate_time_weather,
)


class TimeWeatherFoundationTests(unittest.TestCase):
    def test_defaults_are_sport_independent(self):
        with tempfile.TemporaryDirectory() as directory:
            self.assertTrue(load_time_weather(directory)['clock_enabled'])
            self.assertFalse(load_time_weather(directory)['weather_enabled'])

    def test_settings_roundtrip(self):
        with tempfile.TemporaryDirectory() as directory:
            settings=copy.deepcopy(DEFAULT_TIME_WEATHER)
            settings['timezone']='America/Los_Angeles'
            settings['time_format']='24h'
            save_time_weather(directory,settings)
            self.assertEqual(load_time_weather(directory),settings)

    def test_invalid_timezone_rejected(self):
        settings=copy.deepcopy(DEFAULT_TIME_WEATHER)
        settings['timezone']='Invalid/NotAZone'
        with self.assertRaises(ValueError):
            validate_time_weather(settings)

    def test_clock_renders_in_both_formats(self):
        now=datetime(2026,10,15,22,42,tzinfo=timezone.utc)
        twelve=ClockScreen('America/New_York','12h',now).render()
        twentyfour=ClockScreen('America/New_York','24h',now).render()
        self.assertEqual((twelve.width,twelve.height),(64,32))
        self.assertNotEqual(twelve.pixels,twentyfour.pixels)

    def test_clock_renders_without_weather(self):
        frame=ClockScreen(now=datetime(2026,10,15,tzinfo=timezone.utc)).render()
        self.assertTrue(any(rgb!=(0,0,0) for row in frame.pixels for rgb in row))


if __name__=='__main__':
    unittest.main()
