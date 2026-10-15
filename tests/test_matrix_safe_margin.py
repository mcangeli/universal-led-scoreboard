import unittest
from datetime import datetime
from zoneinfo import ZoneInfo

from universal_led.clock_screen import ClockScreen
from universal_led.weather_screen import WeatherScreen
from universal_led.weather_feed import WeatherSnapshot


class MatrixSafeMarginTests(unittest.TestCase):
    def assert_clear_border(self,frame):
        black=(0,0,0)
        for y,row in enumerate(frame.pixels):
            for x,pixel in enumerate(row):
                if x<2 or x>=62 or y<2 or y>=30:
                    self.assertEqual(pixel,black,(x,y))

    def test_clock_has_clear_border(self):
        clock=ClockScreen(now=datetime(2026,10,15,15,29,tzinfo=ZoneInfo('America/New_York')))
        self.assert_clear_border(clock.render())

    def test_weather_has_clear_border(self):
        weather=WeatherSnapshot('Kennesaw',87,88,61,0,'now')
        self.assert_clear_border(WeatherScreen(weather).render())


if __name__=='__main__':
    unittest.main()
