"""WNBA settings migration and four-sport router checks."""
import copy
import unittest
from universal_led.sport_settings import DEFAULT_SETTINGS, validate_settings
from universal_led.multisport_runtime import MultiSportRenderer


class Stub:
    def __init__(self, name):
        self.name = name
    def frame(self):
        return self.name
    def game(self):
        return None


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


if __name__ == "__main__":
    unittest.main()
