import unittest
from universal_led.weather_feed import BackgroundWeather, WeatherSnapshot


class WeatherCacheInvalidationTests(unittest.TestCase):
    def test_invalidate_forces_refetch(self):
        calls = []
        def fetch(location, unit):
            calls.append(location)
            return WeatherSnapshot(location, 70, 75, 60, 0, 'now')
        cache = BackgroundWeather(fetch=fetch)
        cache.update('Atlanta')
        cache.update('Atlanta')
        self.assertEqual(len(calls), 1)
        cache.invalidate()
        self.assertIsNone(cache.snapshot())
        cache.update('Atlanta')
        self.assertEqual(len(calls), 2)


if __name__ == '__main__':
    unittest.main()
