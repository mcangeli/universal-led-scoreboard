"""Multisport dashboard controls regression checks."""
import unittest
from universal_led.configurator import HTML


class NHLDashboardTests(unittest.TestCase):
    def test_independent_sport_controls(self):
        self.assertIn('id="mlb-enabled"', HTML)
        self.assertIn('id="nhl-enabled"', HTML)
        self.assertNotIn('id="active-sport"', HTML)

    def test_nhl_fields_present(self):
        for field in ("nhl-enabled", "nhl-teams", "nhl-mode",
                      "nhl-rotation", "nhl-refresh"):
            with self.subTest(field=field):
                self.assertIn('id="' + field + '"', HTML)

    def test_save_payload_includes_both_sports(self):
        self.assertIn("next.sports.mlb.enabled=", HTML)
        self.assertIn("next.sports.nhl.enabled=", HTML)
        self.assertIn("next.nhl.favorite_teams=", HTML)
        self.assertIn("Enable at least one sport.", HTML)

    def test_dashboard_reads_saved_values(self):
        self.assertIn("settings.nhl", HTML)
        self.assertIn("settings.sports.mlb.enabled", HTML)
        self.assertIn("settings.sports.nhl.enabled", HTML)


if __name__ == "__main__":
    unittest.main()
