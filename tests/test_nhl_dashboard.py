"""Multisport dashboard controls regression checks."""
import unittest
from universal_led.configurator import HTML


class NHLDashboardTests(unittest.TestCase):
    def test_independent_sport_controls(self):
        self.assertIn('id="mlb-enabled"', HTML)
        self.assertIn('id="nhl-enabled"', HTML)
        self.assertNotIn('id="active-sport"', HTML)

    def test_mlb_and_nhl_controls_share_sports_page(self):
        sports = HTML.split('<section data-page="sports"', 1)[1].split('<section data-page="display"', 1)[0]
        display = HTML.split('<section data-page="display"', 1)[1]
        for field in ('mlb-enabled', 'nhl-enabled', 'mode', 'rotation', 'refresh',
                      'live-classic', 'live-matchup', 'nhl-mode', 'nhl-rotation', 'nhl-refresh'):
            with self.subTest(field=field):
                self.assertIn('id="' + field + '"', sports)
                self.assertNotIn('id="' + field + '"', display)

    def test_nhl_favorites_use_team_checkboxes(self):
        self.assertIn('id="nhl-teams" class="favorite-team-grid"', HTML)
        self.assertIn('value="BOS"', HTML)
        self.assertIn('value="NYR"', HTML)
        self.assertIn('value="UTA"', HTML)
        self.assertIn('function getNHLFavorites()', HTML)
        self.assertIn('setNHLFavorites(nhl.favorite_teams)', HTML)
        self.assertIn('next.nhl.favorite_teams=getNHLFavorites()', HTML)
        self.assertNotIn("document.getElementById('nhl-teams').value=", HTML)

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
