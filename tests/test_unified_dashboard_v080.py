"""Unified dashboard presentation guardrails for v0.8.0."""
import inspect
import unittest
from universal_led import configurator


class UnifiedDashboardTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.source = inspect.getsource(configurator)

    def test_overview_counts_every_supported_sport(self):
        self.assertIn("['mlb','nhl','nba','wnba','nfl','mls','nwsl','english'].filter", self.source)
        self.assertIn("enabled.length+' enabled sports: '", self.source)
        self.assertIn("favorites.length+' favorites'", self.source)

    def test_mlb_diagnostics_not_presented_as_global_feed_health(self):
        self.assertIn('MLB Feed Diagnostics', self.source)
        self.assertIn("'No game selected'", self.source)
        self.assertNotIn("'No MLB game selected'", self.source)


if __name__ == '__main__':
    unittest.main()
