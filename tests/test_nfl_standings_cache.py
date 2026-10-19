"""NFL standings background cache integration contract."""
import tempfile
import unittest

from universal_led.football_standings_runtime import FootballStandingsCache
from universal_led.nfl_standings_feed import fetch_nfl_division, parse_nfl_standings


class NFLStandingsCacheTests(unittest.TestCase):
    def test_division_cache_persists_and_restores_without_network(self):
        payload = {"children": [{"children": [
            {"name": "AFC East", "standings": {"entries": [
                {"team": {"id": "2", "abbreviation": "BUF"}, "stats": [
                    {"name": "wins", "value": 5},
                    {"name": "losses", "value": 1},
                    {"name": "ties", "value": 0}]}]}}]}]}
        rows = parse_nfl_standings(payload)
        calls = []
        def fetcher(league):
            calls.append(league)
            return fetch_nfl_division("AFC East", fetcher=lambda _: rows)
        with tempfile.TemporaryDirectory() as directory:
            cache = FootballStandingsCache(
                "NFL", fetcher=fetcher, cache_dir=directory,
                cache_key="nfl-afc-east", expected_group="AFC East")
            self.assertEqual(cache.refresh()[0].abbreviation, "BUF")
            self.assertEqual(calls, ["NFL"])
            restored = FootballStandingsCache(
                "NFL", fetcher=lambda _: self.fail("unexpected network call"),
                cache_dir=directory, cache_key="nfl-afc-east",
                expected_group="AFC East")
            self.assertEqual(restored.rows(), cache.rows())

    def test_wrong_division_cannot_replace_cache(self):
        from universal_led.standings import Standing
        wrong = Standing(league="NFL", group="NFC East", team_id="DAL",
                         played=1, wins=1, losses=0, rank=1)
        cache = FootballStandingsCache(
            "NFL", fetcher=lambda _: [wrong], expected_group="AFC East")
        self.assertEqual(cache.refresh(), ())
        self.assertIn("different league or group", cache.last_error)


if __name__ == "__main__":
    unittest.main()
