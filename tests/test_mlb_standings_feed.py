"""Offline MLB standings parser regression tests."""
import unittest
from universal_led.mlb_standings_feed import (
    DIVISION_KEYS, fetch_mlb_standings, parse_mlb_standings,
)


class MLBStandingsFeedTests(unittest.TestCase):
    def test_six_official_divisions(self):
        self.assertEqual(set(DIVISION_KEYS.values()), {
            "AL_EAST", "AL_CENTRAL", "AL_WEST",
            "NL_EAST", "NL_CENTRAL", "NL_WEST"})

    def test_official_rank_and_record(self):
        payload = {"records": [{"division": {"id": 204}, "teamRecords": [
            {"team": {"id": 144}, "divisionRank": "2", "wins": 91, "losses": 71},
            {"team": {"id": 121}, "divisionRank": "1", "wins": 94, "losses": 68},
        ]}]}
        rows = parse_mlb_standings(payload)
        self.assertEqual(len(rows), 2)
        self.assertEqual((rows[0].group, rows[0].abbreviation, rows[0].rank),
                         ("NL_EAST", "ATL", 2))
        self.assertEqual(rows[1].rank, 1)
        self.assertEqual(rows[0].played, 162)

    def test_incomplete_rank_is_not_invented(self):
        payload = {"records": [{"division": {"id": 201}, "teamRecords": [
            {"team": {"id": 147}, "wins": 50, "losses": 40},
        ]}]}
        self.assertEqual(parse_mlb_standings(payload), ())

    def test_fetcher_uses_standings_endpoint(self):
        urls = []
        def fetch(url):
            urls.append(url)
            return {"records": []}
        self.assertEqual(fetch_mlb_standings(season=2026, fetch=fetch), ())
        self.assertIn("season=2026", urls[0])
        self.assertIn("/standings?", urls[0])


if __name__ == "__main__":
    unittest.main()
