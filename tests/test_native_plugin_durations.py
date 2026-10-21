"""Regression coverage for native supplemental slot timing and live preemption."""
import unittest
from universal_led.multisport_runtime import MultiSportRenderer


class GameRenderer:
    def __init__(self):
        self.live = False

    def has_live_games(self):
        return self.live

    def frame(self):
        return "game"


class Plugin:
    def __init__(self, label, duration):
        self.label = label
        self.display_seconds = duration
        self.calls = 0

    def frame(self, **kwargs):
        self.calls += 1
        return self.label


class PluginDurationTests(unittest.TestCase):
    def setUp(self):
        self.now = [0]
        self.game = GameRenderer()
        self.board = MultiSportRenderer(self.game, None, clock=lambda: self.now[0])
        self.a = Plugin("first", 5)
        self.b = Plugin("second", 20)
        self.board.set_bullpen_slots((self.a, self.b))

    def test_different_durations_and_cycle_boundaries(self):
        # Cycle: game 0-12, first 12-17, game 17-29,
        # second 29-49; repeat every 49 seconds.
        for moment, expected in ((0, "game"), (11.99, "game"),
                                 (12, "first"), (16.99, "first"),
                                 (17, "game"), (28.99, "game"),
                                 (29, "second"), (36.99, "second"),
                                 (48.99, "second"), (49, "game"),
                                 (60.99, "game"), (61, "first"),
                                 (66, "game"), (78, "second")):
            with self.subTest(moment=moment):
                self.now[0] = moment
                self.assertEqual(self.board.frame(), expected)

    def test_live_game_preempts_plugins(self):
        self.now[0] = 18
        self.game.live = True
        self.assertEqual(self.board.frame(), "game")
        self.assertEqual(self.a.calls, 0)
        self.assertEqual(self.b.calls, 0)

    def test_updated_duration_changes_next_selection(self):
        self.now[0] = 29
        self.assertEqual(self.board.frame(), "second")
        self.a.display_seconds = 10
        # Extending the first plugin shifts the following base slot,
        # so this same timestamp now belongs to regular content.
        self.assertEqual(self.board.frame(), "game")
        self.now[0] = 34
        self.assertEqual(self.board.frame(), "second")


if __name__ == "__main__":
    unittest.main()
