"""MLS standings parser regression tests."""
import unittest
from universal_led.mls_standings_feed import parse_mls_standings


class MLSStandingsTests(unittest.TestCase):
    def test_conference_records(self):
        payload = {"children": [
            {"name": "Eastern Conference", "standings": {"entries": [
                {"team": {"id": "1", "abbreviation": "ATL"},
                 "stats": [{"name": k, "value": v} for k, v in
                           {"wins": 12, "losses": 5, "ties": 7,
                            "gamesPlayed": 24, "points": 43,
                            "rank": 2, "pointDifferential": 9}.items()]}]}},
            {"name": "Western Conference", "standings": {"entries": [
                {"team": {"id": "2", "abbreviation": "LA"},
                 "stats": [{"name": k, "value": v} for k, v in
                           {"wins": 10, "losses": 8, "ties": 6,
                            "gamesPlayed": 24, "points": 36}.items()]}]}}
        ]}
        rows = parse_mls_standings(payload)
        self.assertEqual(len(rows), 2)
        self.assertEqual((rows[0].league, rows[0].group, rows[0].rank,
                          rows[0].wins, rows[0].draws, rows[0].points),
                         ("MLS", "Eastern Conference", 2, 12, 7, 43))
        self.assertEqual(rows[1].group, "Western Conference")

    def test_bad_payload(self):
        with self.assertRaises(ValueError):
            parse_mls_standings([])
