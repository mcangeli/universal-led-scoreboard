"""Main scheduler accepts English football without affecting older sports."""
import unittest
from types import SimpleNamespace

from universal_led.multisport_runtime import MultiSportRenderer


class FakeRenderer:
    def __init__(self, live=False, available=True):
        self.live = live
        self.available = available

    def has_games(self):
        return self.available

    def has_live_games(self):
        return self.live

    def game(self):
        return SimpleNamespace(status="live" if self.live else "pre")

    def frame(self):
        return "frame"


class EnglishMainSchedulerTests(unittest.TestCase):
    def test_english_is_opt_in(self):
        board = MultiSportRenderer(FakeRenderer(), FakeRenderer())
        self.assertNotIn("english", board._supported())

    def test_english_supported_when_provided(self):
        board = MultiSportRenderer(FakeRenderer(), FakeRenderer(), english_renderer=FakeRenderer())
        self.assertIn("english", board._supported())

    def test_live_english_preempts_scheduled_mlb(self):
        board = MultiSportRenderer(FakeRenderer(), FakeRenderer(), english_renderer=FakeRenderer(live=True))
        board.configure_rotation(("mlb", "english"))
        self.assertEqual(board._selected(), "english")

    def test_disabled_english_does_not_preempt(self):
        board = MultiSportRenderer(FakeRenderer(), FakeRenderer(), english_renderer=FakeRenderer(live=True))
        board.configure_rotation(("mlb",))
        self.assertEqual(board._selected(), "mlb")

    def test_english_without_games_is_skipped(self):
        board = MultiSportRenderer(FakeRenderer(), FakeRenderer(), english_renderer=FakeRenderer(available=False))
        board.configure_rotation(("mlb", "english"))
        self.assertEqual(board._selected(), "mlb")

    def test_english_live_suppresses_news(self):
        class News:
            def items(self):
                return [SimpleNamespace(source="test", text="headline")]
        board = MultiSportRenderer(FakeRenderer(), FakeRenderer(), news=News(),
                                  settings_getter=lambda: {"news": {"rotation_interval": 1, "scroll_chars_per_second": 1}},
                                  english_renderer=FakeRenderer(live=True))
        board.configure_rotation(("mlb", "english"))
        self.assertEqual(board.frame(), "frame")


if __name__ == "__main__":
    unittest.main()
