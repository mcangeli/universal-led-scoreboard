"""Additional 0.9.2 coverage for soccer and MLB favorite-final transitions."""
import tempfile
import unittest
from types import SimpleNamespace
from unittest.mock import patch

from universal_led.soccer_rotation import eligible_matches
from universal_led.runtime_settings import ConfiguredMLBRenderer
from universal_led.mlb_classic import BaseballGame


class Feed:
    def __init__(self, games):
        self.current = games

    def games(self):
        return self.current


def soccer_game(home, away, status):
    return SimpleNamespace(home_id=home, away_id=away, home_club_key=None,
                           away_club_key=None, status=status)


class LiveFallbackOtherSportsTests(unittest.TestCase):
    def test_soccer_favorite_final_keeps_two_other_live_games(self):
        games = [soccer_game("ATL", "MIA", "final"),
                 soccer_game("NYC", "PHI", "live"),
                 soccer_game("LA", "SEA", "halftime")]
        self.assertEqual(eligible_matches(games, favorites=["ATL"], mode="fallback"), tuple(games[1:]))
        self.assertEqual(eligible_matches(games, favorites=["ATL"], mode="favorites"), (games[0],))
        self.assertEqual(eligible_matches(games, favorites=["ATL"], mode="all"), tuple(games))

    def test_soccer_live_favorite_stays_first_priority(self):
        games = [soccer_game("ATL", "MIA", "live"), soccer_game("NYC", "PHI", "live")]
        self.assertEqual(eligible_matches(games, favorites=["ATL"], mode="fallback"), (games[0],))

    def test_mlb_favorite_final_keeps_other_live_game(self):
        with tempfile.TemporaryDirectory() as directory:
            favorite = BaseballGame(away="ATL", home="MIA", status="final")
            other = BaseballGame(away="NYM", home="PHI", status="live")
            feed = Feed([favorite, other])
            renderer = ConfiguredMLBRenderer(directory, feed)
            settings = renderer.settings()
            renderer.apply({**settings, "mlb": {**settings["mlb"], "mode": "fallback",
                                               "favorite_teams": ["ATL"]}})
            self.assertTrue(renderer.has_live_games())
            self.assertEqual(renderer.game(), other)
            feed.current[1] = BaseballGame(away="NYM", home="PHI", status="final")
            self.assertFalse(renderer.has_live_games())
            self.assertEqual(renderer.game(), favorite)


if __name__ == "__main__":
    unittest.main()
