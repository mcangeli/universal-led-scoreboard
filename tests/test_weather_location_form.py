"""Time and weather form validation matches location schema limits."""
import unittest
from universal_led import configurator


class WeatherLocationFormTests(unittest.TestCase):
    def test_location_limit_is_checked_before_network_request(self):
        html=configurator.HTML
        start=html.index('async function saveClockSettings(){')
        end=html.index('function showSportsView(',start)
        body=html[start:end]
        self.assertIn("locationInput.value.trim().length>120",body)
        self.assertIn('Weather location must be 120 characters or fewer.',body)
        self.assertLess(body.index('locationInput.focus();'),body.index("fetch('/api/time-weather'"))

    def test_blank_weather_location_is_not_forced(self):
        html=configurator.HTML
        self.assertNotIn('Weather location is required',html)


if __name__=='__main__':
    unittest.main()
