import unittest
from universal_led.nhl_data import parse_game
from universal_led.nhl_engine import ConfiguredNHLRenderer


def game(id, away, home, status="FUT"):
    return parse_game({"id": id, "gameState": status,
                       "awayTeam": {"abbrev": away, "score": 1},
                       "homeTeam": {"abbrev": home, "score": 2}})


class Feed:
    def __init__(self, games):
        self._games = games

    def games(self):
        return list(self._games)


class NHLEngineTests(unittest.TestCase):
    def test_frame_is_native_size(self):
        screen = ConfiguredNHLRenderer(Feed([game(1, "BOS", "NYR")]))
        frame = screen.frame()
        self.assertEqual((frame.width, frame.height), (64, 32))

    def test_rotation_between_games(self):
        now = [0]
        screen = ConfiguredNHLRenderer(
            Feed([game(1, "BOS", "NYR"), game(2, "TOR", "MTL")]),
            mode="all", rotation_seconds=10, clock=lambda: now[0])
        self.assertEqual(screen.game().game_id, 1)
        now[0] = 10
        self.assertEqual(screen.game().game_id, 2)

    def test_live_games_first(self):
        screen = ConfiguredNHLRenderer(
            Feed([game(1, "BOS", "NYR"), game(2, "TOR", "MTL", "LIVE")]),
            mode="all")
        self.assertEqual(screen.game().game_id, 2)

    def test_favorite_only(self):
        screen = ConfiguredNHLRenderer(
            Feed([game(1, "BOS", "NYR"), game(2, "TOR", "MTL")]),
            favorite_teams=["TOR"], mode="favorite")
        self.assertEqual(screen.game().game_id, 2)

    def test_empty_feed_shows_no_game_frame(self):
        screen = ConfiguredNHLRenderer(Feed([]))
        self.assertIsNone(screen.game())
        self.assertEqual(screen.frame().width, 64)

    def test_invalid_settings(self):
        with self.assertRaises(ValueError):
            ConfiguredNHLRenderer(Feed([]), rotation_seconds=0)
        with self.assertRaises(ValueError):
            ConfiguredNHLRenderer(Feed([]), mode="bad")
        with self.assertRaises(ValueError):
            ConfiguredNHLRenderer(Feed([]), favorite_teams=["NOT A TEAM"])


if __name__ == "__main__":
    unittest.main()
