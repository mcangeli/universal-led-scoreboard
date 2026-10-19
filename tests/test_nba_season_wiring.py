"""NBA calendar gating must remain optional until a verified URL is configured."""
import inspect
import unittest

from universal_led import configurator


class NBASeasonWiringTests(unittest.TestCase):
    def test_opt_in_calendar_source(self):
        source = inspect.getsource(configurator.main)
        self.assertIn("ULS_NBA_SEASON_CALENDAR_URL", source)
        self.assertIn("nba_calendar_url.startswith('https://') else None", source)
        self.assertIn("if competition in nba_standings_caches and nba_season_worker is not None:", source)
        self.assertIn("return season_status.eligible('NBA')", source)

    def test_worker_lifecycle(self):
        source = inspect.getsource(configurator.main)
        self.assertIn("if standings_options['enabled'] and selected_nba_conferences:", source)
        self.assertIn("nba_season_worker.start()", source)
        self.assertIn("nba_season_worker.stop()", source)


if __name__ == '__main__':
    unittest.main()
