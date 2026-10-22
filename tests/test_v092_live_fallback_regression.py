"""Regression: completed favorites must not suppress other live fixtures."""
import unittest
from types import SimpleNamespace
from universal_led.nhl_runtime import select_games as nhl_select
from universal_led.nba_runtime import select_games as nba_select
from universal_led.nfl_runtime import select_games as nfl_select


def game(home, away, status):
    return SimpleNamespace(home=home, away=away, status=status)


class LiveFallbackRegressionTests(unittest.TestCase):
    def test_favorite_final_does_not_hide_live_games(self):
        games = [game("BOS", "NYR", "final"), game("TOR", "MTL", "live"),
                 game("DET", "CHI", "live")]
        for name, selector in (("nhl", nhl_select), ("nba", nba_select), ("nfl", nfl_select)):
            with self.subTest(sport=name):
                self.assertEqual(selector(games, ["BOS"], "fallback"), games[1:])
                self.assertEqual(selector(games, ["BOS"], "favorite"), games[:1])
                self.assertEqual(selector(games, ["BOS"], "all"), games)

    def test_live_favorite_still_has_priority(self):
        games = [game("BOS", "NYR", "live"), game("TOR", "MTL", "live")]
        for selector in (nhl_select, nba_select, nfl_select):
            self.assertEqual(selector(games, ["BOS"], "fallback"), games[:1])

    def test_no_live_retains_favorite_fallback(self):
        games = [game("BOS", "NYR", "final"), game("TOR", "MTL", "final")]
        for selector in (nhl_select, nba_select, nfl_select):
            self.assertEqual(selector(games, ["BOS"], "fallback"), games[:1])
            self.assertEqual(selector(games, ["DAL"], "fallback"), games)
