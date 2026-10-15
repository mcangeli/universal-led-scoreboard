import unittest
from urllib.parse import urlsplit, parse_qs
from universal_led.weather_feed import BackgroundWeather, WeatherSnapshot, fetch_weather, weather_description


class WeatherProviderTests(unittest.TestCase):
    def test_fetch_current_and_daily(self):
        urls=[]
        def get_json(url):
            urls.append(url)
            if 'geocoding' in url:
                return {'results':[{'name':'Atlanta','latitude':33.75,'longitude':-84.39}]}
            return {'current':{'temperature_2m':72,'weather_code':2,'time':'2026-10-15T15:00'},
                    'daily':{'temperature_2m_max':[77],'temperature_2m_min':[56]}}
        result=fetch_weather('Atlanta','fahrenheit',get_json=get_json)
        self.assertEqual((result.temperature,result.high,result.low),(72,77,56))
        self.assertEqual(result.location,'Atlanta')
        self.assertEqual(parse_qs(urlsplit(urls[1]).query)['temperature_unit'],['fahrenheit'])

    def test_missing_location(self):
        with self.assertRaises(ValueError):
            fetch_weather('',get_json=lambda url:{})

    def test_geocoding_miss(self):
        with self.assertRaises(ValueError):
            fetch_weather('NotAPlace',get_json=lambda url:{'results':[]})

    def test_cache_and_failed_refresh(self):
        now=[100.]
        calls=[0]
        def fetch(location,unit):
            calls[0]+=1
            if calls[0]>1:raise OSError('offline')
            return WeatherSnapshot(location,70,75,60,0,'2026-10-15')
        cache=BackgroundWeather(fetch=fetch,clock=lambda:now[0],refresh_seconds=60)
        first=cache.update('Atlanta')
        self.assertEqual(cache.update('Atlanta'),first)
        self.assertEqual(calls[0],1)
        now[0]=161
        self.assertEqual(cache.update('Atlanta'),first)
        self.assertEqual(calls[0],2)
        self.assertEqual(cache.error,'offline')

    def test_conditions(self):
        self.assertEqual(weather_description(0),'CLEAR')
        self.assertEqual(weather_description(95),'STORMS')


if __name__=='__main__':
    unittest.main()
