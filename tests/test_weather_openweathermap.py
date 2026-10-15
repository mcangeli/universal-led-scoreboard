import unittest
from urllib.parse import parse_qs, urlsplit
from universal_led.weather_openweathermap import fetch_openweathermap


class OpenWeatherMapTests(unittest.TestCase):
    def test_requires_key(self):
        with self.assertRaises(ValueError):
            fetch_openweathermap('Atlanta')

    def test_current_conditions_normalized(self):
        urls=[]
        def get_json(url):
            urls.append(url)
            return {'name':'Atlanta','dt':1792100000,
                    'main':{'temp':70,'temp_min':65,'temp_max':74},
                    'weather':[{'id':500}]}
        result=fetch_openweathermap('Atlanta','fahrenheit','test-key',get_json=get_json)
        self.assertEqual((result.temperature,result.high,result.low,result.weather_code),(70,74,65,61))
        params=parse_qs(urlsplit(urls[0]).query)
        self.assertEqual(params['units'],['imperial'])
        self.assertEqual(params['appid'],['test-key'])

    def test_celsius_units(self):
        def get_json(url):
            self.assertEqual(parse_qs(urlsplit(url).query)['units'],['metric'])
            return {'main':{'temp':20},'weather':[{'id':800}]}
        result=fetch_openweathermap('London','celsius','key',get_json=get_json)
        self.assertEqual(result.weather_code,0)
        self.assertEqual((result.high,result.low),(20,20))

    def test_invalid_unit(self):
        with self.assertRaises(ValueError):
            fetch_openweathermap('Atlanta','kelvin','key')


if __name__=='__main__':
    unittest.main()
