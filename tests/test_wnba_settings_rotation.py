"""WNBA settings migration and four-sport router checks."""
import copy
import unittest
from types import SimpleNamespace
from universal_led.sport_settings import DEFAULT_SETTINGS, validate_settings
from universal_led.multisport_runtime import MultiSportRenderer


class Stub:
    def __init__(self, name, games=True):
        self.name = name
        self.games = games
    def frame(self):
        return self.name
    def game(self):
        return SimpleNamespace(status="scheduled") if self.games else None


class WNBASettingsRotationTests(unittest.TestCase):
    def test_existing_settings_upgrade(self):
        old = copy.deepcopy(DEFAULT_SETTINGS)
        old["sports"].pop("wnba")
        old.pop("wnba")
        upgraded = validate_settings(old)
        self.assertFalse(upgraded["sports"]["wnba"]["enabled"])
        self.assertEqual(upgraded["wnba"]["favorite_teams"], [])

    def test_enable_wnba(self):
        value = copy.deepcopy(DEFAULT_SETTINGS)
        value["sports"]["wnba"]["enabled"] = True
        value["active_sport"] = "wnba"
        self.assertEqual(validate_settings(value)["active_sport"], "wnba")

    def test_four_sport_rotation(self):
        now = [0]
        board = MultiSportRenderer(Stub("mlb"), Stub("nhl"), clock=lambda: now[0],
                                   nba_renderer=Stub("nba"), wnba_renderer=Stub("wnba"))
        board.configure_rotation(["mlb", "nhl", "nba", "wnba"], interval=10)
        self.assertEqual(board.frame(), "mlb")
        now[0] = 10
        self.assertEqual(board.frame(), "nhl")
        now[0] = 20
        self.assertEqual(board.frame(), "nba")
        now[0] = 30
        self.assertEqual(board.frame(), "wnba")

    def test_empty_league_skipped_without_consuming_slot(self):
        now = [0]
        board = MultiSportRenderer(Stub("mlb"), Stub("nhl", games=False),
                                   nba_renderer=Stub("nba"), wnba_renderer=Stub("wnba", games=False),
                                   clock=lambda: now[0])
        board.configure_rotation(["mlb", "nhl", "nba", "wnba"], interval=10)
        self.assertEqual(board.frame(), "mlb")
        now[0] = 10
        self.assertEqual(board.frame(), "nba")
        now[0] = 20
        self.assertEqual(board.frame(), "mlb")

    def test_all_empty_returns_blank_frame(self):
        board = MultiSportRenderer(Stub("mlb", games=False), Stub("nhl", games=False))
        board.configure_rotation(["mlb", "nhl"])
        frame = board.frame()
        self.assertEqual((frame.width, frame.height), (64, 32))
        self.assertIsNone(board.game())

    def test_finished_game_remains_eligible(self):
        finished = Stub("final")
        finished.game = lambda: SimpleNamespace(status="final")
        board = MultiSportRenderer(finished, Stub("nhl", games=False))
        board.configure_rotation(["mlb", "nhl"])
        self.assertEqual(board.frame(), "final")


if __name__ == "__main__":
    unittest.main()
