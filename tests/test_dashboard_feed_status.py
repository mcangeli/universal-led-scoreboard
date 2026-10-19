"""Regression coverage for dashboard feed timestamp normalization."""
import unittest
from universal_led.configurator import dashboard_feed_status


class DashboardFeedStatusTests(unittest.TestCase):
    def test_monotonic_success_converts_to_unix_seconds(self):
        original={'state':'running','games':0,'last_success':480.0}
        result=dashboard_feed_status(original,wall_now=1_700_000_000.0,monotonic_now=500.0)
        self.assertEqual(result['last_success'],1_699_999_980.0)
        self.assertEqual(result['games'],0)
        self.assertEqual(original['last_success'],480.0)

    def test_mlb_unix_success_is_preserved(self):
        result=dashboard_feed_status({'last_success':1_700_000_000.0},unix_time=True,
                                     wall_now=1_800_000_000.0,monotonic_now=500.0)
        self.assertEqual(result['last_success'],1_700_000_000.0)

    def test_uninitialized_feed_stays_uninitialized(self):
        result=dashboard_feed_status({'state':'starting','last_success':None},
                                     wall_now=1_700_000_000.0,monotonic_now=500.0)
        self.assertIsNone(result['last_success'])
        self.assertEqual(result['state'],'starting')


if __name__=='__main__':
    unittest.main()
