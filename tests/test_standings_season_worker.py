import unittest
from datetime import datetime, timezone

from universal_led.standings_season_status import StandingsSeasonStatus
from universal_led.standings_season_worker import SeasonCalendarWorker


class SeasonCalendarWorkerTests(unittest.TestCase):
    def setUp(self):
        self.now = [datetime(2026, 6, 1, tzinfo=timezone.utc)]
        self.status = StandingsSeasonStatus()
        self.calls = []
        def fetch(competition):
            self.calls.append(competition)
            return [{'phase': 'regular', 'start': '2026-04-01T00:00:00Z',
                     'end': '2026-10-01T00:00:00Z'}]
        self.worker = SeasonCalendarWorker(
            'AL_EAST', fetch, self.status, clock=lambda: self.now[0])

    def test_background_refresh_marks_regular_season(self):
        self.assertEqual(self.worker.refresh(), 'regular')
        self.assertTrue(self.status.eligible('AL_EAST'))
        self.assertEqual(self.calls, ['AL_EAST'])

    def test_boundary_transition_requires_no_network(self):
        self.worker.refresh()
        self.now[0] = datetime(2026, 11, 1, tzinfo=timezone.utc)
        self.assertEqual(self.worker.tick(), 'unknown')
        self.assertFalse(self.status.eligible('AL_EAST'))
        self.assertEqual(len(self.calls), 1)

    def test_failed_refresh_preserves_last_confirmed_state(self):
        self.worker.refresh()
        self.worker.fetcher = lambda _: (_ for _ in ()).throw(OSError('offline'))
        self.assertEqual(self.worker.refresh(), 'unknown')
        self.assertTrue(self.status.eligible('AL_EAST'))
        self.assertEqual(self.worker.last_error, 'offline')

    def test_invalid_calendar_cannot_activate_standings(self):
        self.worker.fetcher = lambda _: []
        self.assertEqual(self.worker.refresh(), 'unknown')
        self.assertFalse(self.status.eligible('AL_EAST'))

    def test_independent_competition_status(self):
        self.worker.refresh()
        self.assertEqual(self.status.phase('EPL'), 'unknown')

    def test_valid_calendar_outside_coverage_invalidates_previous_state(self):
        self.worker.refresh()
        self.now[0] = datetime(2027, 1, 1, tzinfo=timezone.utc)
        self.assertEqual(self.worker.refresh(), 'unknown')
        self.assertFalse(self.status.eligible('AL_EAST'))


if __name__ == '__main__':
    unittest.main()
