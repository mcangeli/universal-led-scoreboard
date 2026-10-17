"""Cached MLB live-status regression coverage for multisport rotation."""
import unittest
from types import SimpleNamespace

from universal_led.runtime_settings import ConfiguredMLBRenderer


class MLBAllGamesLiveTests(unittest.TestCase):
    def setUp(self):
        self.games = [
            SimpleNamespace(status="pregame", away="ATL", home="NYM"),
            SimpleNamespace(status="live", away="LAD", home="SF"),
        ]
        self.mode = "fallback"
        self.renderer = SimpleNamespace(
            feed=SimpleNamespace(games=lambda: self.games),
            settings=lambda: {"mlb": {
                "mode": self.mode,
                "favorite_teams": ["ATL"],
            }},
        )

    def live(self):
        return ConfiguredMLBRenderer.has_live_games(self.renderer)

    def test_fallback_sees_other_live_game(self):
        self.assertTrue(self.live())

    def test_all_mode_sees_other_live_game(self):
        self.mode = "all"
        self.assertTrue(self.live())

    def test_favorite_mode_ignores_unrelated_live_game(self):
        self.mode = "favorite"
        self.assertFalse(self.live())

    def test_favorite_mode_sees_favorite_live_game(self):
        self.mode = "favorite"
        self.games[0].status = "live"
        self.assertTrue(self.live())

    def test_live_status_clears_after_final(self):
        self.assertTrue(self.live())
        self.games[1].status = "final"
        self.assertFalse(self.live())

    def test_empty_schedule_has_no_live_games(self):
        self.games.clear()
        self.assertFalse(self.live())


    def test_frame_skips_supplemental_sources_during_live_game(self):
        from unittest.mock import patch

        game = SimpleNamespace(status="live")
        renderer = SimpleNamespace(
            directory="/unused",
            _selection=lambda: (game, 0),
            has_live_games=lambda: True,
        )
        with patch("universal_led.runtime_settings.read_config", return_value={
            "teams": {}, "scoreboard": {},
        }), patch("universal_led.runtime_settings.load_time_weather",
                  side_effect=AssertionError("supplemental settings queried")), \
             patch("universal_led.runtime_settings.MLBPaletteScreen") as screen:
            screen.return_value.render.return_value = "GAME"
            self.assertEqual(ConfiguredMLBRenderer.frame(renderer), "GAME")
            screen.assert_called_once()

    def test_frame_skips_supplemental_sources_when_another_game_is_live(self):
        from unittest.mock import patch

        game = SimpleNamespace(status="pregame")
        renderer = SimpleNamespace(
            directory="/unused",
            _selection=lambda: (game, 0),
            has_live_games=lambda: True,
        )
        with patch("universal_led.runtime_settings.read_config", return_value={
            "teams": {}, "scoreboard": {},
        }), patch("universal_led.runtime_settings.load_time_weather",
                  side_effect=AssertionError("supplemental settings queried")), \
             patch("universal_led.runtime_settings.MLBPaletteScreen") as screen:
            screen.return_value.render.return_value = "GAME"
            self.assertEqual(ConfiguredMLBRenderer.frame(renderer), "GAME")
            screen.assert_called_once()


if __name__ == "__main__":
    unittest.main()
