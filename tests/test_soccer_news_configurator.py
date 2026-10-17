"""Regression checks for MLS and NWSL news toggles on the News Feeds page."""
import unittest

from universal_led.configurator import HTML


class SoccerNewsConfiguratorTests(unittest.TestCase):
    def test_news_page_has_separate_mls_and_nwsl_checkboxes(self):
        for league in ("mls", "nwsl"):
            self.assertIn('type="checkbox" id="' + league + '-news-enabled"', HTML)

    def test_news_page_loads_saved_soccer_flags(self):
        for league in ("mls", "nwsl"):
            self.assertIn(
                "document.getElementById('" + league + "-news-enabled').checked=data.sports." +
                league + ".news_enabled;", HTML)

    def test_news_page_saves_soccer_flags(self):
        for league in ("mls", "nwsl"):
            self.assertIn(
                "data.sports." + league + ".news_enabled=document.getElementById('" +
                league + "-news-enabled').checked;", HTML)


if __name__ == "__main__":
    unittest.main()
