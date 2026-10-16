import unittest
from universal_led.multisport_runtime import MultiSportRenderer


class FakeRenderer:
    def __init__(self, label):
        self.label = label
    def frame(self):
        return self.label
    def game(self):
        return self.label


class NHLSharedRotationTests(unittest.TestCase):
    def setUp(self):
        self.now = [0]
        self.board = MultiSportRenderer(FakeRenderer("MLB"), FakeRenderer("NHL"),
                                        clock=lambda: self.now[0])

    def test_both_sports_rotate(self):
        self.board.configure_rotation(["mlb", "nhl"], interval=12)
        self.assertEqual(self.board.frame(), "MLB")
        self.now[0] = 12
        self.assertEqual(self.board.frame(), "NHL")
        self.now[0] = 24
        self.assertEqual(self.board.frame(), "MLB")

    def test_only_mlb_preserves_existing_renderer(self):
        self.board.configure_rotation(["mlb"], interval=12)
        self.now[0] = 120
        self.assertEqual(self.board.frame(), "MLB")

    def test_only_nhl(self):
        self.board.configure_rotation(["nhl"], interval=12, preferred="nhl")
        self.assertEqual(self.board.frame(), "NHL")

    def test_bad_configuration_rejected(self):
        with self.assertRaises(ValueError):
            self.board.configure_rotation([])
        with self.assertRaises(ValueError):
            self.board.configure_rotation(["mlb"], interval=0)

    def test_legacy_active_sport_still_works(self):
        self.board.set_active_sport("nhl")
        self.assertEqual(self.board.frame(), "NHL")


if __name__ == "__main__":
    unittest.main()
