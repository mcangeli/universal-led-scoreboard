import unittest
from datetime import datetime, timezone
from universal_led.weather_openweathermap import fetch_openweathermap


class DailyForecastTests(unittest.TestCase):
    def test_local_day_forecast_replaces_current_period_extremes(self):
        # UTC 01:00 is still the previous day at UTC-5.
        now=int(datetime(2026,10,16,1,tzinfo=timezone.utc).timestamp())
        previous=int(datetime(2026,10,15,19,tzinfo=timezone.utc).timestamp())
        same_day=int(datetime(2026,10,16,3,tzinfo=timezone.utc).timestamp())
        tomorrow=int(datetime(2026,10,16,8,tzinfo=timezone.utc).timestamp())
        def get_json(url):
            if '/forecast?' in url:
                return {'city':{'timezone':-18000},'list':[
                    {'dt':previous,'main':{'temp':70,'temp_min':62,'temp_max':83}},
                    {'dt':same_day,'main':{'temp':65,'temp_min':60,'temp_max':75}},
                    {'dt':tomorrow,'main':{'temp':80,'temp_min':40,'temp_max':99}}]}
            return {'name':'Atlanta','dt':now,'timezone':-18000,
                    'main':{'temp':70,'temp_min':69,'temp_max':71},
                    'weather':[{'id':800}]}
        result=fetch_openweathermap('Atlanta','fahrenheit','key',get_json=get_json)
        self.assertEqual((result.temperature,result.high,result.low),(70,83,60))

    def test_forecast_failure_preserves_current_conditions(self):
        def get_json(url):
            if '/forecast?' in url:
                raise OSError('forecast unavailable')
            return {'name':'Atlanta','dt':1792100000,
                    'main':{'temp':70,'temp_min':66,'temp_max':74},
                    'weather':[{'id':800}]}
        result=fetch_openweathermap('Atlanta','fahrenheit','key',get_json=get_json)
        self.assertEqual((result.temperature,result.high,result.low),(70,74,66))


if __name__=='__main__':
    unittest.main()
