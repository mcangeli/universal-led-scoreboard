import unittest
from types import SimpleNamespace

from universal_led.multisport_runtime import MultiSportRenderer
from universal_led.ticker import TickerItem


class Renderer:
    def __init__(self, status=None):
        self.status = status
        self.frames = 0

    def game(self):
        return SimpleNamespace(status=self.status) if self.status else None

    def frame(self):
        self.frames += 1
        return "game-frame"


class News:
    def __init__(self, items):
        self._items = items

    def items(self):
        return self._items


class UniversalNewsRotationTests(unittest.TestCase):
    def make_board(self, now, mlb_status=None, nhl_status=None, items=None):
        mlb, nhl = Renderer(mlb_status), Renderer(nhl_status)
        settings = {"news": {"rotation_interval": 2, "headline_seconds": 12, "scroll_chars_per_second": 3}}
        board = MultiSportRenderer(mlb, nhl, clock=lambda: now[0],
                                  news=News(items or []), settings_getter=lambda: settings)
        board.configure_rotation(["mlb", "nhl"], interval=10)
        return board, mlb, nhl

    def test_all_sources_share_the_same_news_screen(self):
        now = [10]
        items = [TickerItem("mlb", "MLB headline"), TickerItem("nhl", "NHL headline"),
                 TickerItem("AP", "AP headline")]
        board, _, _ = self.make_board(now, items=items)
        # The universal renderer returns the same framebuffer type for each source.
        frames = []
        for moment in (10, 30, 50):
            now[0] = moment
            frames.append(board.frame())
        self.assertTrue(all(hasattr(frame, "ppm") for frame in frames))
        self.assertEqual(len({frame.ppm() for frame in frames}), 3)

    def test_live_game_not_interrupted(self):
        now = [10]
        board, mlb, nhl = self.make_board(now, mlb_status="live", nhl_status="live",
                                          items=[TickerItem("AP", "AP headline")])
        self.assertEqual(board.frame(), "game-frame")
        self.assertEqual(nhl.frames, 1)
        now[0] = 20
        self.assertEqual(board.frame(), "game-frame")
        self.assertEqual(mlb.frames, 1)

    def test_no_news_uses_game_renderer(self):
        now = [10]
        board, _, nhl = self.make_board(now)
        self.assertEqual(board.frame(), "game-frame")
        self.assertEqual(nhl.frames, 1)


if __name__ == "__main__":
    unittest.main()
