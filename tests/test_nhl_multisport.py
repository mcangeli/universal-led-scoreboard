import unittest
from universal_led.multisport_runtime import MultiSportRenderer


class FakeRenderer:
    def __init__(self, label):
        self.label = label
        self.calls = []

    def frame(self):
        self.calls.append("frame")
        return self.label

    def game(self):
        self.calls.append("game")
        return self.label + "-game"


class MultiSportTests(unittest.TestCase):
    def setUp(self):
        self.mlb = FakeRenderer("MLB")
        self.nhl = FakeRenderer("NHL")
        self.router = MultiSportRenderer(self.mlb, self.nhl)

    def test_default_is_mlb(self):
        self.assertEqual(self.router.active_sport, "mlb")
        self.assertEqual(self.router.frame(), "MLB")

    def test_switch_to_nhl(self):
        self.router.set_active_sport("nhl")
        self.assertEqual(self.router.frame(), "NHL")
        self.assertEqual(self.router.game(), "NHL-game")

    def test_switch_back_to_mlb(self):
        self.router.set_active_sport("nhl")
        self.router.set_active_sport("mlb")
        self.assertEqual(self.router.frame(), "MLB")

    def test_invalid_sport_does_not_change_selection(self):
        with self.assertRaises(ValueError):
            self.router.set_active_sport("nfl")
        self.assertEqual(self.router.active_sport, "mlb")

    def test_no_cross_sport_render(self):
        self.router.set_active_sport("nhl")
        self.router.frame()
        self.assertEqual(self.mlb.calls, [])
        self.assertEqual(self.nhl.calls, ["frame"])


if __name__ == "__main__":
    unittest.main()
