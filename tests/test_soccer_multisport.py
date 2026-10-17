import unittest

from universal_led.multisport_runtime import MultiSportRenderer


class FakeRenderer:
    def __init__(self, live=False, games=True):
        self.live = live
        self.games = games
        self.calls = []

    def has_games(self):
        return self.games

    def has_live_games(self):
        return self.live

    def frame(self):
        self.calls.append("frame")
        return "frame"

    def game(self):
        return None


class SoccerMultisportTests(unittest.TestCase):
    def board(self, **kwargs):
        return MultiSportRenderer(FakeRenderer(), FakeRenderer(), **kwargs)

    def test_mls_is_supported_when_renderer_provided(self):
        board = self.board(mls_renderer=FakeRenderer())
        board.set_active_sport("mls")
        self.assertEqual(board.active_sport, "mls")

    def test_nwsl_is_supported_when_renderer_provided(self):
        board = self.board(nwsl_renderer=FakeRenderer())
        board.set_active_sport("nwsl")
        self.assertEqual(board.active_sport, "nwsl")

    def test_sports_absent_without_renderers(self):
        board = self.board()
        with self.assertRaises(ValueError):
            board.set_active_sport("mls")

    def test_mls_live_priority_over_nonlive_mlb(self):
        mlb = FakeRenderer()
        mls = FakeRenderer(live=True)
        board = MultiSportRenderer(mlb, FakeRenderer(), mls_renderer=mls, clock=lambda: 0)
        board.configure_rotation(["mlb", "mls"], preferred="mlb")
        self.assertEqual(board._selected(), "mls")

    def test_nwsl_live_priority_over_nonlive_mls(self):
        mls = FakeRenderer()
        nwsl = FakeRenderer(live=True)
        board = self.board(mls_renderer=mls, nwsl_renderer=nwsl, clock=lambda: 0)
        board.configure_rotation(["mls", "nwsl"], preferred="mls")
        self.assertEqual(board._selected(), "nwsl")

    def test_soccer_frame_routes_to_selected_renderer(self):
        mls = FakeRenderer()
        board = self.board(mls_renderer=mls)
        board.set_active_sport("mls")
        self.assertEqual(board.frame(), "frame")
        self.assertEqual(mls.calls, ["frame"])

    def test_no_soccer_games_skipped_in_rotation(self):
        mls = FakeRenderer(games=False)
        board = self.board(mls_renderer=mls, clock=lambda: 0)
        board.configure_rotation(["mlb", "mls"])
        self.assertEqual(board._selected(), "mlb")


if __name__ == "__main__":
    unittest.main()
