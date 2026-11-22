"""Regression checks: Opening Day must not be starved by global idle pages."""
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from universal_led.display import Framebuffer
from universal_led.multisport_runtime import MultiSportRenderer


class StubMLB:
    def __init__(self, directory):
        self.directory = directory
        self.opening_feed = object()

    def frame(self):
        frame = Framebuffer()
        frame.pixel(0, 0, (11, 22, 33))
        return frame

    def has_live_games(self):
        return False


class GlobalCountdownRotationTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.mlb = StubMLB(self.tmp.name)
        self.now = [0.]
        self.board = MultiSportRenderer(self.mlb, self.mlb,
                                         clock=lambda: self.now[0])
        self.board.configure_rotation(("mlb",), interval=5)
        self.preferences = {
            "clock_enabled": False, "weather_enabled": False,
            "timezone": "America/New_York", "time_format": "12h",
            "temperature_unit": "F",
        }

    def test_countdown_gets_own_idle_slot(self):
        marker = Framebuffer()
        marker.pixel(0, 0, (88, 99, 111))
        with patch("universal_led.multisport_runtime.load_time_weather",
                   return_value=self.preferences), \\
             patch("universal_led.multisport_runtime.current_countdown",
                   return_value=object()) as current, \\
             patch("universal_led.multisport_runtime.SeasonCountdownScreen") as screen:
            screen.return_value.render.return_value = marker
            self.now[0] = 10
            self.assertEqual(self.board.frame().pixels[0][0], (88, 99, 111))
            current.assert_called()
            screen.return_value.render.assert_called_once()

    def test_missing_countdown_keeps_regular_rotation(self):
        with patch("universal_led.multisport_runtime.load_time_weather",
                   return_value=self.preferences), \\
             patch("universal_led.multisport_runtime.current_countdown",
                   return_value=None):
            self.now[0] = 10
            self.assertEqual(self.board.frame().pixels[0][0], (11, 22, 33))

    def test_live_game_does_not_query_or_render_countdown(self):
        with patch.object(self.mlb, "has_live_games", return_value=True), \\
             patch("universal_led.multisport_runtime.current_countdown") as current:
            self.board.frame()
            current.assert_not_called()


if __name__ == "__main__":
    unittest.main()
