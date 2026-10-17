"""Regression checks for v0.4.5 sports navigation."""
import unittest
from universal_led.configurator import HTML, LOGIN_HTML


class SportsNavigationTests(unittest.TestCase):
    def test_three_task_views(self):
        for name in ("overview", "configure", "rotation"):
            self.assertIn('id="sports-' + name + '"', HTML)
            self.assertIn('data-sports-view="' + name + '"', HTML)

    def test_five_sport_panels(self):
        for name in ("mlb", "nhl", "nba", "wnba", "nfl"):
            with self.subTest(sport=name):
                self.assertIn('data-sport-panel="' + name + '"', HTML)
                self.assertIn('id="sport-state-' + name + '"', HTML)

    def test_existing_save_hook_preserved(self):
        self.assertIn('id="save-settings"', HTML)
        self.assertIn("saveSportSettings('sports')", HTML)

    def test_no_new_sport_css_in_login(self):
        self.assertNotIn('/* v0.4.5 Preview 2:', LOGIN_HTML)
        self.assertIn('/* v0.4.5 Preview 2:', HTML)


if __name__ == "__main__":
    unittest.main()
