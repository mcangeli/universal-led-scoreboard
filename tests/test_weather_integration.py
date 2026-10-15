import tempfile
import unittest
from unittest.mock import Mock

from universal_led.weather_feed import WeatherSnapshot
from universal_led.weather_screen import WeatherScreen
from universal_led.weather_worker import WeatherWorker
from universal_led.time_weather_settings import DEFAULT_TIME_WEATHER, save_time_weather


class WeatherIntegrationTests(unittest.TestCase):
    def setUp(self):
        self.snapshot=WeatherSnapshot('Atlanta',72,79,58,2,'2026-10-15T15:00')

    def test_weather_screen_is_64x32(self):
        frame=WeatherScreen(self.snapshot).render()
        self.assertEqual((frame.width,frame.height),(64,32))
        self.assertTrue(any(pixel!=(0,0,0) for row in frame.pixels for pixel in row))

    def test_units_change_display(self):
        self.assertNotEqual(WeatherScreen(self.snapshot,'fahrenheit').render().pixels,
                            WeatherScreen(self.snapshot,'celsius').render().pixels)

    def test_worker_disabled_does_not_fetch(self):
        with tempfile.TemporaryDirectory() as directory:
            cache=Mock()
            worker=WeatherWorker(directory,cache=cache)
            worker.refresh()
            cache.update.assert_not_called()

    def test_worker_enabled_uses_location(self):
        with tempfile.TemporaryDirectory() as directory:
            settings=dict(DEFAULT_TIME_WEATHER,weather_enabled=True,location='Atlanta',temperature_unit='celsius')
            save_time_weather(directory,settings)
            cache=Mock()
            worker=WeatherWorker(directory,cache=cache)
            worker.refresh()
            cache.update.assert_called_once_with('Atlanta','celsius')


if __name__=='__main__':
    unittest.main()
