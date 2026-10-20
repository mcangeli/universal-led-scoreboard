"""Optional Bullpen attachment must preserve existing MLB rotation."""
import threading
import time
import unittest
from types import SimpleNamespace
from unittest.mock import patch

from universal_led.runtime_settings import ConfiguredMLBRenderer


class Slot:
    def __init__(self):
        self.calls = []

    def frame(self, **kwargs):
        self.calls.append(kwargs)
        return "PLUGIN"


class BullpenMLBIntegrationTests(unittest.TestCase):
    def renderer(self, game, live):
        slot = Slot()
        renderer = SimpleNamespace(
            directory="/unused",
            _selection=lambda: (game, 0),
            has_live_games=lambda: live,
            bullpen_slot=slot,
            _lock=threading.Lock(),
            _started=time.monotonic(),
            _supplemental_stride=1,
            settings=lambda: {"mlb": {"rotation_seconds": 12}},
            weather=None,
            news=None,
            opening_feed=None,
        )
        return renderer, slot

    def test_live_game_does_not_invoke_plugin(self):
        renderer, slot = self.renderer(SimpleNamespace(status="live"), True)
        with patch("universal_led.runtime_settings.read_config", return_value={"teams": {}, "scoreboard": {}}), \
             patch("universal_led.runtime_settings.MLBPaletteScreen") as screen:
            screen.return_value.render.return_value = "GAME"
            self.assertEqual(ConfiguredMLBRenderer.frame(renderer), "GAME")
        self.assertEqual(slot.calls, [])

    def test_pregame_does_not_invoke_plugin(self):
        renderer, slot = self.renderer(SimpleNamespace(status="pregame"), False)
        with patch("universal_led.runtime_settings.read_config", return_value={"teams": {}, "scoreboard": {}}), \
             patch("universal_led.runtime_settings.load_time_weather", return_value={"clock_enabled": False, "weather_enabled": False}), \
             patch("universal_led.runtime_settings.current_countdown", return_value=None), \
             patch("universal_led.runtime_settings.choose_screen", return_value="game"), \
             patch("universal_led.runtime_settings.MLBPaletteScreen") as screen:
            screen.return_value.render.return_value = "PREGAME"
            self.assertEqual(ConfiguredMLBRenderer.frame(renderer), "PREGAME")
        self.assertEqual(slot.calls, [])

    def test_empty_schedule_can_display_plugin(self):
        renderer, slot = self.renderer(None, False)
        with patch("universal_led.runtime_settings.read_config", return_value={"teams": {}, "scoreboard": {}}), \
             patch("universal_led.runtime_settings.load_time_weather", side_effect=AssertionError("should return plugin first")):
            self.assertEqual(ConfiguredMLBRenderer.frame(renderer), "PLUGIN")
        self.assertEqual(slot.calls, [{"live_games": False, "selected": True}])


if __name__ == "__main__":
    unittest.main()
