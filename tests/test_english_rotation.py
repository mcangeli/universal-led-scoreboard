"""Regression tests for combined English football rotation."""
import unittest
from types import SimpleNamespace

from universal_led.english_rotation import EnglishFootballRenderer
from universal_led.soccer import SoccerMatch


def match(league, team, status="pre"):
    return SoccerMatch(f"{league}-{team}", league, team, "OPP", 0, 0, status,
                       home_club_key=f"espn:{team}")


def feed(*games):
    return SimpleNamespace(games=lambda: list(games))


class EnglishRotationTests(unittest.TestCase):
    def test_live_in_second_division_overrides_scheduled_epl(self):
        renderer = EnglishFootballRenderer({
            "EPL": feed(match("EPL", "1")),
            "CHAMPIONSHIP": feed(match("CHAMPIONSHIP", "2", "in"))})
        self.assertEqual(renderer.game().league, "CHAMPIONSHIP")
        self.assertTrue(renderer.has_live_games())

    def test_disabled_division_does_not_show(self):
        renderer = EnglishFootballRenderer({
            "EPL": feed(match("EPL", "1")),
            "LEAGUE_TWO": feed(match("LEAGUE_TWO", "2", "in"))},
            enabled=("EPL",))
        self.assertEqual(renderer.game().league, "EPL")
        self.assertFalse(renderer.has_live_games())

    def test_stable_favorite_crosses_divisions(self):
        renderer = EnglishFootballRenderer({
            "EPL": feed(match("EPL", "381")),
            "LEAGUE_ONE": feed(match("LEAGUE_ONE", "999"))},
            favorite_teams=("espn:381",), mode="favorite")
        self.assertEqual(renderer.game().home_id, "381")

    def test_live_rotation_cycles_between_divisions(self):
        now = [0]
        renderer = EnglishFootballRenderer({
            "EPL": feed(match("EPL", "1", "in")),
            "LEAGUE_ONE": feed(match("LEAGUE_ONE", "2", "in"))},
            rotation_seconds=10, clock=lambda: now[0])
        self.assertEqual(renderer.game().league, "EPL")
        now[0] = 11
        self.assertEqual(renderer.game().league, "LEAGUE_ONE")

    def test_empty_enabled_set(self):
        renderer = EnglishFootballRenderer({"EPL": feed(match("EPL", "1"))}, enabled=())
        self.assertFalse(renderer.has_games())
        self.assertIsNone(renderer.game())

    def test_unknown_competition_rejected(self):
        with self.assertRaises(ValueError):
            EnglishFootballRenderer({"FA_CUP": feed()})

    def test_wrong_league_feed_ignored(self):
        renderer = EnglishFootballRenderer({"EPL": feed(match("CHAMPIONSHIP", "1"))})
        self.assertFalse(renderer.has_games())

    def test_no_feed_network_call_from_render(self):
        class Cached:
            def games(self):
                return [match("EPL", "1")]
            def refresh(self, *args):
                raise AssertionError("Rendering must not poll ESPN")
        renderer = EnglishFootballRenderer({"EPL": Cached()})
        self.assertEqual(renderer.game().league, "EPL")


if __name__ == "__main__":
    unittest.main()
