"""Shared scheduler standings priority regression tests."""
import unittest
from types import SimpleNamespace

from universal_led.display import Framebuffer
from universal_led.multisport_runtime import MultiSportRenderer
from universal_led.scoring_alerts import ScoringAlerts, ScoreEvent


class Renderer:
    def __init__(self, games=False, live=False):
        self.games = games
        self.live = live
    def game(self):
        return None
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

    def test_idle_news_and_standings_both_receive_slots(self):
        now = [0]
        class News:
            def items(self):
                return [SimpleNamespace(source="SPORT", text="NEWS")]
        standings = Standings()
        standings.page_seconds = 3
        board = MultiSportRenderer(
            Renderer(), Renderer(), clock=lambda: now[0],
            news=News(), settings_getter=lambda: {"news": {
                "rotation_interval": 99, "scroll_chars_per_second": 1}},
            standings_rotation=standings)
        first = board.frame().pixels
        self.assertEqual(first[0][0], (4, 5, 6))
        now[0] = 3
        second = board.frame().pixels
        self.assertNotEqual(first, second)
        self.assertEqual(standings.calls, 1)
        now[0] = 6
        self.assertEqual(board.frame().pixels[0][0], (4, 5, 6))
        self.assertEqual(standings.calls, 2)

    def test_scoring_alert_interrupts_standings_then_restores_them(self):
        now = [0]
        alerts = ScoringAlerts(enabled=True, scope="all", seconds=3)
        event = ScoreEvent("soccer", "EPL", "game-1", "goal-1", "ARS", "GOAL")
        alerts.observe("soccer", "EPL", "game-1", [])
        alerts.observe("soccer", "EPL", "game-1", [event])
        standings = Standings()
        def alert_frame(_event):
            frame = Framebuffer()
            frame.pixel(0, 0, (9, 8, 7))
            return frame
        board = MultiSportRenderer(Renderer(), Renderer(),
                                   clock=lambda: now[0],
                                   scoring_alerts=alerts,
                                   alert_renderer=alert_frame,
                                   standings_rotation=standings)
        self.assertEqual(board.frame().pixels[0][0], (9, 8, 7))
        self.assertEqual(standings.calls, 0)
        now[0] = 3
        self.assertEqual(board.frame().pixels[0][0], (4, 5, 6))
        self.assertEqual(standings.calls, 1)

    def test_idle_news_supports_renderer_without_game_method(self):
        now = [3]
        class News:
            def items(self):
                return [SimpleNamespace(source="SPORT", text="NEWS")]
        class NoGameRenderer:
            def has_games(self):
                return False
            def has_live_games(self):
                return False
            def frame(self):
                return Framebuffer()
        standings = Standings()
        standings.page_seconds = 3
        board = MultiSportRenderer(
            NoGameRenderer(), NoGameRenderer(), clock=lambda: now[0],
            news=News(), settings_getter=lambda: {"news": {
                "rotation_interval": 99, "scroll_chars_per_second": 1}},
            standings_rotation=standings)
        board._started = 0
        frame = board.frame()
        self.assertEqual((frame.width, frame.height), (64, 32))
        self.assertEqual(standings.calls, 0)

    def test_disabled_standings_preserve_blank_fallback(self):
        board = MultiSportRenderer(Renderer(), Renderer(), standings_rotation=Standings(False))
        self.assertEqual(board.frame().pixels[0][0], (1, 2, 3))

    def test_no_standings_adapter_preserves_existing_behavior(self):
        board = MultiSportRenderer(Renderer(), Renderer())
        self.assertEqual(board.frame().pixels[0][0], (1, 2, 3))


if __name__ == "__main__":
    unittest.main()
