"""English football standings feed contract tests."""
import unittest
from unittest.mock import patch
from io import BytesIO

from universal_led.football_standings_feed import (
    fetch_football_standings, parse_football_standings,
)


def entry(team, rank, points, gd):
    return {"team": {"id": team}, "stats": [
        {"name": "gamesPlayed", "value": 5},
        {"name": "wins", "value": 3},
        {"name": "losses", "value": 1},
        {"name": "ties", "value": 1},
        {"name": "points", "value": points},
        {"name": "pointDifferential", "value": gd},
        {"name": "rank", "value": rank},
    ]}


class FootballStandingsFeedTests(unittest.TestCase):
    def test_parse_official_positions_and_groups(self):
        data = {"children": [{"name": "Premier League", "standings": {
            "entries": [entry("10", 2, 10, 4), entry("20", 1, 12, 7)]}}]}
        rows = parse_football_standings(data, "EPL")
        self.assertEqual([r.team_id for r in rows], ["10", "20"])
        self.assertEqual([r.rank for r in rows], [2, 1])
        self.assertEqual(rows[0].group, "Premier League")

    def test_missing_team_identity_is_skipped(self):
        data = {"standings": {"entries": [{"team": {}, "stats": []}]}}
        self.assertEqual(parse_football_standings(data, "EPL"), ())

    def test_rejects_unknown_league(self):
        with self.assertRaises(ValueError):
            parse_football_standings({}, "NBA")
        with self.assertRaises(ValueError):
            fetch_football_standings("NBA")

    def test_rejects_invalid_timeout_before_network(self):
        with self.assertRaises(ValueError):
            fetch_football_standings("EPL", timeout=0)

    def test_fetch_uses_correct_competition_and_normalizes(self):
        import json
        payload = json.dumps({"standings": {"entries": [entry("1", 1, 10, 3)]}}).encode()
        class Response(BytesIO):
            def __enter__(self):
                return self
            def __exit__(self, *args):
                self.close()
        with patch("universal_led.football_standings_feed.urlopen", return_value=Response(payload)) as mock:
            rows = fetch_football_standings("EPL")
        self.assertEqual(rows[0].team_id, "1")
        self.assertIn("/eng.1/standings", mock.call_args.args[0].full_url)


if __name__ == "__main__":
    unittest.main()
