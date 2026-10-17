"""Dashboard English football controls stay connected to saved settings."""
import unittest
from universal_led.configurator import HTML


class EnglishDashboardTests(unittest.TestCase):
    def test_english_sport_card_and_panel(self):
        self.assertIn('sport-state-english', HTML)
        self.assertIn('data-sport-panel="english"', HTML)
        self.assertIn('id="english-enabled"', HTML)

    def test_all_four_divisions_are_selectable(self):
        for league in ('EPL', 'CHAMPIONSHIP', 'LEAGUE_ONE', 'LEAGUE_TWO'):
            with self.subTest(league=league):
                self.assertIn('value="'+league+'"', HTML)

    def test_settings_are_loaded_and_saved(self):
        for fragment in ("settings.sports.english.enabled",
                         "english.enabled_leagues.includes(el.value)",
                         "next.sports.english.enabled=",
                         "next.english.enabled_leagues=",
                         "next.english.rotation_seconds=",
                         "next.english.refresh_seconds="):
            with self.subTest(fragment=fragment):
                self.assertIn(fragment, HTML)

    def test_english_is_in_overview_and_picker(self):
        self.assertIn('<option value="english">English Football</option>', HTML)
        self.assertIn("['mlb','nhl','nba','wnba','nfl','mls','nwsl','english'].forEach", HTML)


if __name__ == "__main__":
    unittest.main()
