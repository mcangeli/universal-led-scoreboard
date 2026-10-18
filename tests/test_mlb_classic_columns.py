"""Pixel-level R/H/E alignment regression tests for the 64x32 MLB board."""
import unittest

from universal_led.mlb_classic import BaseballGame, MLBClassicScreen, GOLD


class MLBClassicColumnsTests(unittest.TestCase):
    def test_headers_centered_in_separate_columns(self):
        frame = MLBClassicScreen().render()
        for x in (43, 51, 59):
            self.assertTrue(any(frame.pixels[y][col] == GOLD
                                for y in range(1, 6) for col in range(x, x+3)))

    def test_single_digit_values_right_aligned(self):
        frame = MLBClassicScreen(BaseballGame(away_runs=1, away_hits=2,
                                              away_errors=3)).render()
        for x in (45, 53, 61):
            self.assertTrue(any(frame.pixels[y][col] != (0, 0, 0)
                                for y in range(9, 14) for col in range(x, x+3)))
        for x in (41, 49, 57):
            self.assertTrue(all(frame.pixels[y][x] == (0, 0, 0)
                                for y in range(9, 14)))

    def test_double_digit_values_fit_all_three_columns(self):
        frame = MLBClassicScreen(BaseballGame(away_runs=12, away_hits=15,
                                              away_errors=10)).render()
        for x in (41, 49, 57):
            self.assertTrue(any(frame.pixels[y][col] != (0, 0, 0)
                                for y in range(9, 14) for col in range(x, x+3)))
        self.assertEqual((frame.width, frame.height), (64, 32))


if __name__ == "__main__":
    unittest.main()
