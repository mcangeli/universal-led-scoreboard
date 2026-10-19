import unittest
from datetime import date
from universal_led.nhl_season_calendar import parse_nhl_season_windows


class NHLSeasonCalendarTests(unittest.TestCase):
    def test_two_calendar_year_season(self):
        payload = {'data': [{'id': 20262027, 'regularSeasonStartDate': '2026-10-07',
                             'regularSeasonEndDate': '2027-04-15'}]}
        windows = parse_nhl_season_windows(payload, today=date(2026, 10, 19))
        self.assertEqual(windows, [{'phase': 'regular', 'start': '2026-10-07T00:00:00Z',
                                    'end': '2027-04-16T00:00:00Z'}])
        self.assertEqual(windows, parse_nhl_season_windows(payload, today=date(2027, 2, 1)))

    def test_invalid_response(self):
        with self.assertRaises(ValueError):
            parse_nhl_season_windows({'data': None})

    def test_missing_dates_are_not_guessed(self):
        with self.assertRaises(ValueError):
            parse_nhl_season_windows({'data': [{'id': 20262027}]}, today=date(2026, 10, 19))

    def test_other_seasons_are_ignored(self):
        with self.assertRaises(ValueError):
            parse_nhl_season_windows({'data': [{'id': 20242025, 'regularSeasonStartDate': '2024-10-01',
                                                 'regularSeasonEndDate': '2025-04-15'}]},
                                     today=date(2026, 10, 19))


if __name__ == '__main__':
    unittest.main()
