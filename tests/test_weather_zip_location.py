import unittest
from urllib.parse import urlsplit, parse_qs
from universal_led.weather_openweathermap import fetch_openweathermap
from universal_led.weather_screen import WeatherScreen


class ZipLocationTests(unittest.TestCase):
    def test_zip_resolves_city_and_state(self):
        urls=[]
        def get_json(url):
            urls.append(url)
            if '/geo/1.0/zip?' in url:
                return {'name':'Kennesaw','lat':34.02,'lon':-84.61}
            if '/geo/1.0/reverse?' in url:
                return [{'name':'Kennesaw','state':'Georgia','country':'US'}]
            return {'main':{'temp':70},'weather':[{'id':800}],'name':'Kennesaw'}
        snapshot=fetch_openweathermap('30144','fahrenheit','key',get_json=get_json)
        self.assertEqual(snapshot.location,'Kennesaw, GA')
        self.assertEqual(len(urls),3)
        self.assertIn('lat',parse_qs(urlsplit(urls[1]).query))
        self.assertTrue(any(pixel!=(0,0,0) for row in WeatherScreen(snapshot).render().pixels for pixel in row))

    def test_zip_reverse_failure_keeps_city(self):
        def get_json(url):
            if '/geo/1.0/zip?' in url:
                return {'name':'Kennesaw','lat':34.02,'lon':-84.61}
            if '/geo/1.0/reverse?' in url:
                raise OSError('offline')
            return {'main':{'temp':70},'weather':[{'id':800}]}
        self.assertEqual(fetch_openweathermap('30144','fahrenheit','key',get_json=get_json).location,'Kennesaw')


if __name__=='__main__':
    unittest.main()
