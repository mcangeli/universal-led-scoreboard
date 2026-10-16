"""NBA multisport wiring regressions without network or Pi hardware."""
import copy
import unittest
from universal_led.sport_settings import DEFAULT_SETTINGS, validate_settings
from universal_led.multisport_runtime import MultiSportRenderer


class Stub:
    def __init__(self, sport):
        self.sport = sport
    def frame(self):
        return self.sport
    def game(self):
        return None


class NBAIntegrationTests(unittest.TestCase):
    def test_nba_settings_enabled(self):
        settings = copy.deepcopy(DEFAULT_SETTINGS)
        settings["sports"]["nba"]["enabled"] = True
        settings["active_sport"] = "nba"
        self.assertEqual(validate_settings(settings)["active_sport"], "nba")

    def test_nba_settings_legacy(self):
        settings = copy.deepcopy(DEFAULT_SETTINGS)
        settings.pop("nba")
        self.assertEqual(validate_settings(settings)["nba"]["mode"], "fallback")

    def test_nba_rotation(self):
        now = [0]
        board = MultiSportRenderer(Stub("mlb"), Stub("nhl"), clock=lambda: now[0], nba_renderer=Stub("nba"))
        board.configure_rotation(["mlb", "nhl", "nba"], interval=10, preferred="mlb")
        self.assertEqual(board.frame(), "mlb")
        now[0] = 10
        self.assertEqual(board.frame(), "nhl")
        now[0] = 20
        self.assertEqual(board.frame(), "nba")

    def test_nba_not_allowed_without_renderer(self):
        board = MultiSportRenderer(Stub("mlb"), Stub("nhl"))
        with self.assertRaises(ValueError):
            board.set_active_sport("nba")


if __name__ == "__main__":
    unittest.main()
