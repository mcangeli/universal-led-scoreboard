import unittest
from datetime import datetime, timezone

from universal_led.standings_season_calendar import parse_season_windows, season_phase


class StandingsSeasonCalendarTests(unittest.TestCase):
    def setUp(self):
        self.windows = parse_season_windows([
            {'phase': 'regular', 'start': '2026-04-01T00:00:00Z',
             'end': '2026-10-01T00:00:00Z'},
            {'phase': 'postseason', 'start': '2026-10-01T00:00:00Z',
             'end': '2026-11-01T00:00:00Z'}])

    def test_regular_season(self):
        self.assertEqual(season_phase(self.windows, datetime(2026, 7, 1, tzinfo=timezone.utc)), 'regular')

    def test_postseason(self):
        self.assertEqual(season_phase(self.windows, datetime(2026, 10, 15, tzinfo=timezone.utc)), 'postseason')

    def test_uncovered_date_is_unknown_not_offseason(self):
        self.assertEqual(season_phase(self.windows, datetime(2027, 1, 1, tzinfo=timezone.utc)), 'unknown')

    def test_end_is_exclusive(self):
        self.assertEqual(season_phase(self.windows, datetime(2026, 11, 1, tzinfo=timezone.utc)), 'unknown')

    def test_overlapping_windows_rejected(self):
        with self.assertRaises(ValueError):
            parse_season_windows([
                {'phase': 'regular', 'start': '2026-01-01T00:00:00Z',
                 'end': '2026-10-01T00:00:00Z'},
                {'phase': 'postseason', 'start': '2026-09-01T00:00:00Z',
                 'end': '2026-11-01T00:00:00Z'}])

    def test_naive_dates_rejected(self):
        with self.assertRaises(ValueError):
            parse_season_windows([{'phase': 'regular', 'start': '2026-01-01T00:00:00',
                                   'end': '2026-02-01T00:00:00'}])

    def test_empty_calendar_is_unknown(self):
        self.assertEqual(season_phase((), datetime(2026, 7, 1, tzinfo=timezone.utc)), 'unknown')


if __name__ == '__main__':
    unittest.main()
