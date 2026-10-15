import unittest
from pathlib import Path
from universal_led.configurator import HTML


class TimezoneSelectTests(unittest.TestCase):
    def test_timezone_is_select_not_free_text(self):
        self.assertIn('<select id="clock-timezone">',HTML)
        self.assertNotIn('<input id="clock-timezone"',HTML)

    def test_us_timezones_and_utc_available(self):
        for zone in ('America/New_York','America/Chicago','America/Denver',
                     'America/Phoenix','America/Los_Angeles','America/Anchorage',
                     'Pacific/Honolulu','UTC'):
            with self.subTest(zone=zone):
                self.assertIn('value="'+zone+'"',HTML)

    def test_saved_custom_timezone_preserved(self):
        self.assertIn("customOption.value=data.timezone",HTML)
        self.assertIn("zoneSelect.value=data.timezone",HTML)


if __name__=='__main__':
    unittest.main()
