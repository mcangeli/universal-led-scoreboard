"""NHL dashboard controls regression checks."""
import unittest
from universal_led.configurator import HTML


class NHLDashboardTests(unittest.TestCase):
    def test_active_sport_control(self):
        self.assertIn('id="active-sport"', HTML)
        self.assertIn('<option value="nhl">NHL</option>', HTML)

    def test_nhl_fields_present(self):
        for field in ("nhl-enabled", "nhl-teams", "nhl-mode",
                      "nhl-rotation", "nhl-refresh"):
            with self.subTest(field=field):
                self.assertIn('id="' + field + '"', HTML)

    def test_save_payload_includes_nhl(self):
        self.assertIn("next.sports.nhl.enabled=", HTML)
        self.assertIn("next.nhl.favorite_teams=", HTML)
        self.assertIn("next.active_sport=", HTML)

    def test_dashboard_reads_saved_values(self):
        self.assertIn("settings.nhl", HTML)
        self.assertIn("settings.active_sport", HTML)


if __name__ == "__main__":
    unittest.main()
