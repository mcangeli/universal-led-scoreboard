"""Dashboard wiring regressions for the opt-in soccer leagues."""
import inspect
import unittest
from universal_led import configurator


class SoccerConfiguratorIntegrationTests(unittest.TestCase):
    def test_both_leagues_have_sport_cards_and_panels(self):
        html = configurator.HTML
        for league in ("mls", "nwsl"):
            with self.subTest(league=league):
                self.assertIn('sport-state-'+league, html)
                self.assertIn('data-sport-panel="'+league+'"', html)
                self.assertIn('id="'+league+'-enabled"', html)
                self.assertIn('id="'+league+'-provider"', html)

    def test_source_options_are_exposed(self):
        html = configurator.HTML
        for value in ("league_first", "league_only", "espn_only"):
            self.assertIn('value="'+value+'"', html)

    def test_persisted_soccer_controls_are_loaded_and_saved(self):
        html = configurator.HTML
        self.assertIn("next.sports[league].enabled=", html)
        self.assertIn("next[league].favorite_teams=", html)
        self.assertIn("options.favorite_teams.join(', ')", html)

    def test_soccer_workers_started_and_stopped(self):
        source = inspect.getsource(configurator.main)
        self.assertIn("soccer_workers[league].start()", source)
        self.assertIn("worker.stop()", source)
        self.assertIn("mls_renderer=soccer_renderers['mls']", source)
        self.assertIn("nwsl_renderer=soccer_renderers['nwsl']", source)

    def test_existing_mlb_default_remains(self):
        from universal_led.sport_settings import DEFAULT_SETTINGS
        self.assertEqual(DEFAULT_SETTINGS['active_sport'], 'mlb')
        self.assertFalse(DEFAULT_SETTINGS['sports']['mls']['enabled'])
        self.assertFalse(DEFAULT_SETTINGS['sports']['nwsl']['enabled'])


if __name__ == "__main__":
    unittest.main()
