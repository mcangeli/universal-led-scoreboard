import io
import json
import unittest

from universal_led.mlb_season_calendar import parse_mlb_season_windows, fetch_mlb_season_windows
from universal_led.standings_season_calendar import parse_season_windows, season_phase
from datetime import datetime, timezone


SAMPLE = {'seasons': [{
    'regularSeasonStartDate': '2026-03-26',
    'regularSeasonEndDate': '2026-09-27',
    'postSeasonEndDate': '2026-11-04',
}]}


class MLBSeasonCalendarTests(unittest.TestCase):
    def test_regular_season_from_official_dates(self):
        windows = parse_season_windows(parse_mlb_season_windows(SAMPLE))
        self.assertEqual(season_phase(windows, datetime(2026, 7, 1, tzinfo=timezone.utc)), 'regular')

    def test_postseason_not_mislabeled_regular(self):
        windows = parse_season_windows(parse_mlb_season_windows(SAMPLE))
        self.assertEqual(season_phase(windows, datetime(2026, 10, 15, tzinfo=timezone.utc)), 'postseason')

    def test_offseason_is_not_stale_regular_season(self):
        windows = parse_season_windows(parse_mlb_season_windows(SAMPLE))
        self.assertEqual(season_phase(windows, datetime(2026, 12, 1, tzinfo=timezone.utc)), 'unknown')

    def test_invalid_payload_rejected(self):
        with self.assertRaises(ValueError):
            parse_mlb_season_windows({'seasons': []})

    def test_official_fetch_uses_injectable_opener(self):
        urls = []
        def opener(url, timeout):
            urls.append(url)
            return io.BytesIO(json.dumps(SAMPLE).encode())
        rows = fetch_mlb_season_windows('AL_EAST', year=2026, opener=opener)
        self.assertEqual(len(rows), 2)
        self.assertIn('sportId=1', urls[0])
        self.assertIn('season=2026', urls[0])


if __name__ == '__main__':
    unittest.main()
