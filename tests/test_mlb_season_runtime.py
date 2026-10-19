"""MLB season calendar wiring must not affect unrelated sports."""
import inspect
import unittest

from universal_led import configurator
from universal_led.standings import Standing
from universal_led.standings_rotation import StandingsRotation
from universal_led.standings_season_status import StandingsSeasonStatus


class FakeCache:
    def __init__(self, row):
        self.row = row

    def rows(self):
        return (self.row,)


class MLBSeasonRuntimeTests(unittest.TestCase):
    def test_runtime_connects_calendar_worker_and_gate(self):
        source = inspect.getsource(configurator.main)
        self.assertIn("SeasonCalendarWorker(", source)
        self.assertIn("'MLB', fetch_mlb_season_windows, season_status", source)
        self.assertIn("season_policy=standings_season_eligible", source)
        self.assertIn("mlb_season_worker.start()", source)
        self.assertIn("mlb_season_worker.stop()", source)

    def test_offseason_mlb_does_not_hide_english_standings(self):
        status = StandingsSeasonStatus()
        status.update('MLB', 'offseason')
        caches = {
            'AL_EAST': FakeCache(Standing('MLB', 'AL_EAST', 'ATL', 20, 12, 8, rank=1)),
            'EPL': FakeCache(Standing('EPL', 'Premier League', 'ARS', 20, 12, 6, 2, rank=1)),
        }
        rotation = StandingsRotation(
            caches, enabled=True,
            season_policy=lambda competition:
                status.eligible('MLB') if competition == 'AL_EAST' else True)
        self.assertEqual(len(rotation._pages()), 1)
        self.assertEqual(rotation._pages()[0][0][0], 'EPL')


if __name__ == '__main__':
    unittest.main()
