"""NFL end-to-end settings, feed selection, and rotation regressions."""
import copy
import unittest
from datetime import date
from types import SimpleNamespace

from universal_led.sport_settings import DEFAULT_SETTINGS, validate_settings
from universal_led.nfl_engine import ConfiguredNFLRenderer
from universal_led.nfl_runtime import BackgroundNFLFeed
from universal_led.multisport_runtime import MultiSportRenderer
from universal_led.nfl_feed import NFLFeed


class Stub:
    def __init__(self, label):
        self.label = label

    def frame(self):
        return self.label

    def game(self):
        return None


class NFLIntegrationTests(unittest.TestCase):
    def test_nfl_can_be_enabled_with_two_letter_favorite(self):
        settings = copy.deepcopy(DEFAULT_SETTINGS)
        settings["sports"]["nfl"]["enabled"] = True
        settings["active_sport"] = "nfl"
        settings["nfl"]["favorite_teams"] = ["ATL", "KC", "SF"]
        self.assertEqual(validate_settings(settings)["active_sport"], "nfl")

    def test_legacy_settings_gain_nfl_defaults(self):
        settings = copy.deepcopy(DEFAULT_SETTINGS)
        del settings["nfl"]
        self.assertEqual(validate_settings(settings)["nfl"], DEFAULT_SETTINGS["nfl"])

    def test_nfl_favorites_and_empty_day(self):
        games = [
            SimpleNamespace(away="ATL", home="CHI", status="scheduled"),
            SimpleNamespace(away="KC", home="SF", status="final"),
        ]
        feed = SimpleNamespace(games=lambda: games)
        nfl = ConfiguredNFLRenderer(feed, favorite_teams=["KC"], mode="favorite")
        self.assertEqual(nfl.game().away, "KC")
        self.assertTrue(nfl.has_games())
        games.clear()
        self.assertIsNone(nfl.game())
        self.assertFalse(nfl.has_games())

    def test_nfl_skipped_when_no_games(self):
        games = []
        nfl = ConfiguredNFLRenderer(SimpleNamespace(games=lambda: games))
        clock = [0]
        board = MultiSportRenderer(Stub("mlb"), Stub("nhl"), nfl_renderer=nfl,
                                   clock=lambda: clock[0])
        board.configure_rotation(["mlb", "nfl"], interval=10)
        self.assertEqual(board.frame(), "mlb")
        games.append(SimpleNamespace(away="ATL", home="CHI", status="scheduled"))
        clock[0] = 10
        self.assertIs(board.game(), games[0])

    def test_background_nfl_feed_uses_local_day(self):
        seen = []
        feed = NFLFeed(fetcher=lambda day: (seen.append(day) or {"events": []}))
        worker = BackgroundNFLFeed(feed, day_provider=lambda: date(2026, 10, 18))
        self.assertEqual(worker.refresh_once(), [])
        self.assertEqual(seen, [date(2026, 10, 18)])


if __name__ == "__main__":
    unittest.main()
