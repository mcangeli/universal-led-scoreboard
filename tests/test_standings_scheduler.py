"""Shared scheduler standings priority regression tests."""
import unittest

from universal_led.display import Framebuffer
from universal_led.multisport_runtime import MultiSportRenderer


class Renderer:
    def __init__(self, games=False, live=False):
        self.games = games
        self.live = live
    def has_games(self):
        return self.games
    def has_live_games(self):
        return self.live
    def frame(self):
        frame = Framebuffer()
        frame.pixel(0, 0, (1, 2, 3))
        return frame


class Standings:
    def __init__(self, enabled=True):
        self.enabled = enabled
        self.calls = 0
    def has_pages(self):
        return self.enabled
    def frame(self):
        self.calls += 1
        frame = Framebuffer()
        frame.pixel(0, 0, (4, 5, 6))
        return frame


class StandingsSchedulerTests(unittest.TestCase):
    def test_idle_standings_take_empty_slot(self):
        standings = Standings()
        board = MultiSportRenderer(Renderer(), Renderer(), standings_rotation=standings)
        self.assertEqual(board.frame().pixels[0][0], (4, 5, 6))
        self.assertEqual(standings.calls, 1)

    def test_scheduled_games_precede_standings(self):
        standings = Standings()
        board = MultiSportRenderer(Renderer(games=True), Renderer(), standings_rotation=standings)
        self.assertEqual(board.frame().pixels[0][0], (1, 2, 3))
        self.assertEqual(standings.calls, 0)

    def test_live_games_precede_standings(self):
        standings = Standings()
        board = MultiSportRenderer(Renderer(games=True, live=True), Renderer(), standings_rotation=standings)
        self.assertEqual(board.frame().pixels[0][0], (1, 2, 3))
        self.assertEqual(standings.calls, 0)

    def test_disabled_standings_preserve_blank_fallback(self):
        board = MultiSportRenderer(Renderer(), Renderer(), standings_rotation=Standings(False))
        self.assertEqual(board.frame().pixels[0][0], (1, 2, 3))

    def test_no_standings_adapter_preserves_existing_behavior(self):
        board = MultiSportRenderer(Renderer(), Renderer())
        self.assertEqual(board.frame().pixels[0][0], (1, 2, 3))


if __name__ == "__main__":
    unittest.main()
