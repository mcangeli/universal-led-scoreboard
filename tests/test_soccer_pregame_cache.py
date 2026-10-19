"""Cached pregame records must not trigger network calls or affect live scores."""
import unittest
from universal_led.soccer import SoccerMatch
from universal_led.standings import Standing
from universal_led.soccer_pregame import with_cached_records
from universal_led.english_rotation import EnglishFootballRenderer


class Cache:
    def rows(self):
        return (Standing("EPL", "EPL", "123", 12, 6, 2, draws=4,
                         abbreviation="ARS"),)


class Feed:
    def games(self):
        return (SoccerMatch("m", "EPL", "ARS", "CHE", 0, 0, "pre",
                            home_club_key="espn:123"),)


class PregameCacheTests(unittest.TestCase):
    def test_matches_by_provider_identity(self):
        game = Feed().games()[0]
        enriched = with_cached_records(game, Cache().rows())
        self.assertEqual(enriched.home_record, "6-4-2")
        self.assertIsNone(enriched.away_record)

    def test_existing_feed_record_wins(self):
        game = SoccerMatch("m", "EPL", "ARS", "CHE", 0, 0, "pre",
                           home_record="7-3-2")
        self.assertEqual(with_cached_records(game, Cache().rows()).home_record, "7-3-2")

    def test_live_match_unchanged(self):
        game = SoccerMatch("m", "EPL", "ARS", "CHE", 2, 1, "in")
        self.assertIs(with_cached_records(game, Cache().rows()), game)

    def test_renderer_uses_supplied_cache_without_refresh(self):
        renderer = EnglishFootballRenderer({"EPL": Feed()},
                                           standings_caches={"EPL": Cache()})
        self.assertEqual(renderer.game().home_record, "6-4-2")


if __name__ == "__main__":
    unittest.main()
