"""Verify standings controls are wired through the native configurator."""
import inspect
import unittest

from universal_led import configurator


class StandingsConfiguratorTests(unittest.TestCase):
    def test_controls_are_present(self):
        for identifier in ("standings-enabled", "standings-page-seconds",
                           "standings-refresh-seconds", "standings-status"):
            self.assertIn('id="' + identifier + '"', configurator.HTML)

    def test_page_loads_standings_preferences(self):
        self.assertIn("loadGameInterruptions();loadStandingsSettings()", configurator.HTML)

    def test_save_uses_authenticated_settings_endpoint(self):
        self.assertIn("async function saveStandingsSettings()", configurator.HTML)
        self.assertIn("data.standings={", configurator.HTML)
        self.assertIn("'X-Configurator-Token':token", configurator.HTML)

    def test_startup_attaches_standings_to_board(self):
        source = inspect.getsource(configurator.main)
        self.assertIn("standings_rotation=standings_rotation", source)
        self.assertIn("standings_workers[league].start()", source)
        self.assertIn("standings_workers[league].stop()", source)


if __name__ == "__main__":
    unittest.main()
