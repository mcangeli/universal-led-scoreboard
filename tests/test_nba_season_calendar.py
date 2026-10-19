import unittest
from datetime import datetime, timezone

from universal_led.nba_season_calendar import parse_nba_season_windows
from universal_led.standings_season_calendar import parse_season_windows, season_phase


class NBASeasonCalendarTests(unittest.TestCase):
    def test_cross_year_regular_season(self):
        payload = {'seasons': [{'regularSeasonStartDate': '2026-10-20',
                                'regularSeasonEndDate': '2027-04-11'}]}
        windows = parse_nba_season_windows(payload)
        self.assertEqual(windows, [{'phase': 'regular',
                                    'start': '2026-10-20T00:00:00Z',
                                    'end': '2027-04-12T00:00:00Z'}])
        parsed = parse_season_windows(windows)
        self.assertEqual(season_phase(parsed, datetime(2027, 2, 1, tzinfo=timezone.utc)), 'regular')
        self.assertEqual(season_phase(parsed, datetime(2027, 6, 1, tzinfo=timezone.utc)), 'unknown')

    def test_missing_dates_do_not_create_a_season(self):
        with self.assertRaises(ValueError):
            parse_nba_season_windows({'seasons': [{'year': 2026}]})

    def test_invalid_boundaries_rejected(self):
        with self.assertRaises(ValueError):
            parse_nba_season_windows({'seasons': [{'regularSeasonStartDate': '2027-05-01',
                                                   'regularSeasonEndDate': '2027-04-01'}]})

    def test_invalid_provider_response_rejected(self):
        with self.assertRaises(ValueError):
            parse_nba_season_windows({'seasons': None})


if __name__ == '__main__':
    unittest.main()
