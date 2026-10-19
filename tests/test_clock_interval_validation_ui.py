"""Shared clock interval validation UI contract."""
import unittest
from universal_led import configurator


class ClockIntervalValidationTests(unittest.TestCase):
    def test_invalid_interval_is_rejected_before_network_save(self):
        html=configurator.HTML
        start=html.index('async function saveClockSettings(){')
        end=html.index('function showSportsView(',start)
        section=html[start:end]
        self.assertIn("intervalInput.value.trim()===''",section)
        self.assertIn('!Number.isInteger(interval)||interval<1||interval>20',section)
        self.assertIn('intervalInput.focus();',section)
        self.assertLess(section.index('intervalInput.focus();'),section.index("fetch('/api/time-weather'"))

    def test_validated_interval_is_used_in_payload(self):
        html=configurator.HTML
        self.assertIn('data.rotation_interval=interval;',html)
        self.assertIn('Clock rotation interval must be a whole number from 1 to 20.',html)


if __name__=='__main__':
    unittest.main()
