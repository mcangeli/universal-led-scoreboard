"""Guard the dashboard's news and standings wiring against release regressions."""
import inspect
import unittest

from universal_led import configurator


class DashboardNewsControlsTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.source = inspect.getsource(configurator)

    def test_premier_league_and_efl_controls_exist(self):
        for league in ("english", "efl"):
            with self.subTest(league=league):
                self.assertIn('id="' + league + '-news-enabled"', self.source)
                self.assertIn("getElementById('" + league + "-news-enabled').checked=data.sports." + league + ".news_enabled", self.source)
                self.assertIn("data.sports." + league + ".news_enabled=document.getElementById('" + league + "-news-enabled').checked", self.source)

    def test_wnba_and_nwsl_standings_controls_exist_on_sport_panels(self):
        for league in ("wnba", "nwsl"):
            with self.subTest(league=league):
                panel = self.source.index('data-sport-panel="' + league + '"')
                checkbox = self.source.index('id="' + league + '-standings-enabled"')
                self.assertGreater(checkbox, panel)
                self.assertLess(checkbox, self.source.index('</fieldset>', panel))
        self.assertIn("next.standings[league]=document.getElementById(league+'-standings-enabled').checked", self.source)
        self.assertIn("settings.standings[league]===true", self.source)


if __name__ == "__main__":
    unittest.main()
