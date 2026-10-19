"""Official NHL standings normalization contract."""
import unittest

from universal_led.nhl_standings_feed import parse_nhl_standings


class NHLStandingsFeedTests(unittest.TestCase):
    def test_division_rank_and_overtime_losses_are_preserved(self):
        payload = {'standings': [
            {'divisionName': {'default': 'Atlantic'}, 'teamAbbrev': {'default': 'FLA'},
             'divisionSequence': 2, 'gamesPlayed': 20, 'wins': 12, 'losses': 5,
             'otLosses': 3, 'points': 27},
            {'divisionName': {'default': 'Metropolitan'}, 'teamAbbrev': {'default': 'NYR'},
             'divisionSequence': 1, 'gamesPlayed': 20, 'wins': 15, 'losses': 4,
             'otLosses': 1, 'points': 31},
        ]}
        rows = parse_nhl_standings(payload)
        self.assertEqual(len(rows), 2)
        self.assertEqual((rows[0].group, rows[0].rank), ('Atlantic', 2))
        self.assertEqual((rows[0].wins, rows[0].losses, rows[0].draws, rows[0].points),
                         (12, 5, 3, 27))
        self.assertEqual(rows[1].group, 'Metropolitan')

    def test_official_fetch_is_injectable_and_filters_divisions(self):
        import io
        import json
        from universal_led.nhl_standings_feed import (
            fetch_nhl_standings, fetch_nhl_division, NHL_STANDINGS_URL)
        payload = {'standings': [
            {'divisionName': 'Atlantic', 'teamAbbrev': {'default': 'BOS'},
             'divisionSequence': 1, 'gamesPlayed': 20, 'wins': 10,
             'losses': 8, 'otLosses': 2, 'points': 22},
            {'divisionName': 'Pacific', 'teamAbbrev': {'default': 'VAN'},
             'divisionSequence': 1, 'gamesPlayed': 20, 'wins': 11,
             'losses': 7, 'otLosses': 2, 'points': 24},
        ]}
        class Response(io.BytesIO):
            def __enter__(self):
                return self
            def __exit__(self, *args):
                self.close()
        calls = []
        def opener(url, *, timeout):
            calls.append((url, timeout))
            return Response(json.dumps(payload).encode())
        rows = fetch_nhl_standings(opener=opener)
        self.assertEqual(len(calls), 1)
        request, timeout = calls[0]
        self.assertEqual(request.full_url, NHL_STANDINGS_URL)
        self.assertEqual(timeout, 12)
        self.assertEqual(request.get_header('Accept'), 'application/json')
        self.assertIn('UniversalLEDScoreboard', request.get_header('User-agent'))
        self.assertEqual([row.group for row in rows], ['Atlantic', 'Pacific'])
        self.assertEqual([row.team_id for row in
                          fetch_nhl_division('Atlantic', fetcher=lambda _: rows)],
                         ['BOS'])
        with self.assertRaises(ValueError):
            fetch_nhl_division('Unknown', fetcher=lambda _: rows)

    def test_invalid_payload_rejected(self):
        with self.assertRaises(ValueError):
            parse_nhl_standings([])
        with self.assertRaises(ValueError):
            parse_nhl_standings({'standings': None})

    def test_incomplete_rows_are_not_fabricated(self):
        self.assertEqual(parse_nhl_standings({'standings': [
            {'teamAbbrev': {'default': 'BOS'}, 'divisionName': 'Atlantic'}
        ]}), ())


if __name__ == '__main__':
    unittest.main()
