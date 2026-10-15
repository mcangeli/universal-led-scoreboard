import unittest
from universal_led.display import Framebuffer
from universal_led.weather_icons import draw_weather_icon


class WeatherIconTests(unittest.TestCase):
    def test_each_condition_draws_pixels(self):
        for code in (0,1,2,3,45,51,61,71,95):
            with self.subTest(code=code):
                frame=Framebuffer()
                draw_weather_icon(frame,1,9,code)
                self.assertTrue(any(pixel!=(0,0,0) for row in frame.pixels for pixel in row))

    def test_sun_and_rain_have_distinct_art(self):
        sun=Framebuffer()
        rain=Framebuffer()
        draw_weather_icon(sun,1,9,0)
        draw_weather_icon(rain,1,9,61)
        self.assertNotEqual(sun.pixels,rain.pixels)


if __name__=='__main__':
    unittest.main()
