"""Regression coverage for the scoring alert configurator controls."""
import unittest
from universal_led.configurator import HTML


class ScoringAlertConfiguratorTests(unittest.TestCase):
    def test_controls_live_on_existing_news_page(self):
        for identifier in ("scoring-alerts-enabled", "scoring-alerts-scope",
                           "scoring-alerts-seconds", "scoring-alerts-status"):
            with self.subTest(identifier=identifier):
                self.assertIn('id="'+identifier+'"', HTML)
        self.assertIn('value="favorites"', HTML)
        self.assertIn('value="all"', HTML)

    def test_news_navigation_loads_alert_preferences(self):
        self.assertIn("loadNewsTiming();loadScoringAlerts()", HTML)

    def test_save_uses_authenticated_existing_settings_endpoint(self):
        self.assertIn("async function saveScoringAlerts()", HTML)
        self.assertIn("data.scoring_alerts=", HTML)
        self.assertIn("'X-Configurator-Token':token", HTML)

    def test_duration_has_client_side_limits(self):
        self.assertIn('id="scoring-alerts-seconds" type="number" min="1" max="60"', HTML)
        self.assertIn("!Number.isInteger(seconds)||seconds<1||seconds>60", HTML)


if __name__ == "__main__":
    unittest.main()
