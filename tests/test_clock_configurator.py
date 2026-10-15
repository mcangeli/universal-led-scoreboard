import unittest
from universal_led.configurator import HTML
from universal_led.time_weather_settings import DEFAULT_TIME_WEATHER, validate_time_weather


class ClockConfiguratorTests(unittest.TestCase):
    def test_clock_controls_are_available(self):
        for marker in ('id="clock-enabled"','id="clock-timezone"','id="clock-format"','id="clock-interval"','saveClockSettings()','/api/time-weather'):
            with self.subTest(marker=marker):
                self.assertIn(marker,HTML)

    def test_weather_controls_remain_disabled(self):
        self.assertIn('id="weather-enabled" type="checkbox" disabled',HTML)

    def test_clock_configuration_is_valid(self):
        settings=dict(DEFAULT_TIME_WEATHER,clock_enabled=True,timezone='America/Chicago',time_format='24h',rotation_interval=3)
        self.assertEqual(validate_time_weather(settings),settings)


if __name__=='__main__':
    unittest.main()
