"""Regression tests for global idle clock/weather scheduling."""
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from universal_led.multisport_runtime import MultiSportRenderer


class FakeRenderer:
    def __init__(self, label, live=False):
        self.label = label
        self.live = live

    def has_games(self):
        return True

    def has_live_games(self):
        return self.live

    def frame(self):
        return self.label


class FakeWeather:
    def __init__(self, snapshot):
        self.value = snapshot

    def snapshot(self):
        return self.value


class FakeScreen:
    def __init__(self, *args):
        self.args = args

    def render(self):
        return "supplemental"


class IdleTimeWeatherTests(unittest.TestCase):
    def make_runtime(self, directory, weather, *, live=False):
        now = [0.0]
        mlb = FakeRenderer("mlb", live=live)
        mlb.directory = directory
        mlb.weather = weather
        nba = FakeRenderer("nba", live=live)
        runtime = MultiSportRenderer(mlb, FakeRenderer("nhl"),
                                     nba_renderer=nba, clock=lambda: now[0])
        runtime.configure_rotation(("mlb", "nba"), interval=10)
        return runtime, now

    def test_clock_and_weather_survive_multisport_idle_rotation(self):
        with tempfile.TemporaryDirectory() as directory:
            Path(directory, "time_weather.json").write_text("{}")
            runtime, now = self.make_runtime(directory, FakeWeather(object()))
            settings = {"clock_enabled": True, "weather_enabled": True,
                        "timezone": "America/New_York", "time_format": "12h",
                        "temperature_unit": "fahrenheit"}
            with patch("universal_led.multisport_runtime.load_time_weather", return_value=settings), \
                 patch("universal_led.multisport_runtime.ClockScreen", FakeScreen), \
                 patch("universal_led.multisport_runtime.WeatherScreen", FakeScreen):
                frames = []
                for second in (0, 10, 20, 30):
                    now[0] = second
                    frames.append(runtime.frame())
            self.assertEqual(frames, ["mlb", "nba", "supplemental", "supplemental"])

    def test_live_games_suppress_idle_clock_and_weather(self):
        with tempfile.TemporaryDirectory() as directory:
            Path(directory, "time_weather.json").write_text("{}")
            runtime, now = self.make_runtime(directory, FakeWeather(object()), live=True)
            now[0] = 20
            with patch("universal_led.multisport_runtime.load_time_weather") as settings:
                self.assertIn(runtime.frame(), ("mlb", "nba"))
                settings.assert_not_called()

    def test_missing_weather_does_not_suppress_clock(self):
        with tempfile.TemporaryDirectory() as directory:
            Path(directory, "time_weather.json").write_text("{}")
            runtime, now = self.make_runtime(directory, FakeWeather(None))
            settings = {"clock_enabled": True, "weather_enabled": True,
                        "timezone": "America/New_York", "time_format": "12h",
                        "temperature_unit": "fahrenheit"}
            now[0] = 20
            with patch("universal_led.multisport_runtime.load_time_weather", return_value=settings), \
                 patch("universal_led.multisport_runtime.ClockScreen", FakeScreen):
                self.assertEqual(runtime.frame(), "supplemental")


if __name__ == "__main__":
    unittest.main()
