import tempfile
import unittest
from unittest.mock import patch

from universal_led.time_weather_settings import DEFAULT_TIME_WEATHER, save_time_weather
from universal_led.weather_credentials import save_openweathermap_key, load_openweathermap_key
from universal_led.weather_feed import BackgroundWeather, WeatherSnapshot
from universal_led.weather_worker import WeatherWorker


class WeatherStabilityTests(unittest.TestCase):
    def setUp(self):
        self.calls=[]
        self.cache=BackgroundWeather(fetch=self.fetch)
        self.snapshot_value=WeatherSnapshot('Atlanta',72,80,60,0,'now')

    def fetch(self,location,unit):
        self.calls.append((location,unit))
        return self.snapshot_value

    def test_provider_change_forces_fetch(self):
        with tempfile.TemporaryDirectory() as directory:
            worker=WeatherWorker(directory,cache=self.cache)
            save_time_weather(directory,dict(DEFAULT_TIME_WEATHER,weather_enabled=True,location='Atlanta'))
            worker.refresh()
            worker.refresh()
            self.assertEqual(len(self.calls),1)
            save_openweathermap_key(directory,'example-key')
            save_time_weather(directory,dict(DEFAULT_TIME_WEATHER,weather_enabled=True,
                                              location='Atlanta',weather_provider='openweathermap'))
            worker.refresh()
            self.assertEqual(len(self.calls),2)
            worker.refresh()
            self.assertEqual(len(self.calls),2)

    def test_key_change_forces_fetch(self):
        with tempfile.TemporaryDirectory() as directory:
            worker=WeatherWorker(directory,cache=self.cache)
            save_time_weather(directory,dict(DEFAULT_TIME_WEATHER,weather_enabled=True,
                                              location='Atlanta',weather_provider='openweathermap'))
            save_openweathermap_key(directory,'first-key')
            worker.refresh()
            save_openweathermap_key(directory,'second-key')
            worker.refresh()
            self.assertEqual(len(self.calls),2)
            self.assertEqual(load_openweathermap_key(directory),'second-key')

    def test_failed_refresh_retains_last_snapshot(self):
        calls=[0]
        def fetch(location,unit):
            calls[0]+=1
            if calls[0]>1:
                raise OSError('network unavailable')
            return self.snapshot_value
        cache=BackgroundWeather(fetch=fetch)
        cache.update('Atlanta')
        cache.invalidate()
        self.assertIsNone(cache.snapshot())
        # An outage without a configuration change retains the cached value.
        cache=BackgroundWeather(fetch=fetch,refresh_seconds=0)
        calls[0]=0
        cache.update('Atlanta')
        self.assertEqual(cache.update('Atlanta'),self.snapshot_value)
        self.assertEqual(cache.snapshot(),self.snapshot_value)


if __name__=='__main__':
    unittest.main()
