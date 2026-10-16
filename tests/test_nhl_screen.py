"""64x32 NHL renderer tests, no API or physical matrix required."""
import unittest
from dataclasses import replace

from universal_led.nhl_data import parse_game
from universal_led.nhl_screen import NHLScreen, status_text


def game(**kwargs):
    obj = {
        "id": 1, "gameState": "LIVE",
        "awayTeam": {"abbrev": "BOS", "score": 2},
        "homeTeam": {"abbrev": "NYR", "score": 1},
        "periodDescriptor": {"number": 3, "periodType": "REG"},
        "clock": {"timeRemaining": "04:32"},
    }
    obj.update(kwargs)
    return parse_game(obj)


class NHLScreenTests(unittest.TestCase):
    def test_native_frame_size(self):
        fb = NHLScreen(game()).render()
        self.assertEqual((fb.width, fb.height), (64, 32))
        self.assertEqual(len(fb.ppm()), len(b"P6\n64 32\n255\n") + 64 * 32 * 3)

    def test_every_state_renders(self):
        for state in ("FUT", "LIVE", "FINAL", "PPD", "OFF"):
            with self.subTest(state=state):
                fb = NHLScreen(game(gameState=state)).render()
                self.assertTrue(any(any(pixel) for row in fb.pixels for pixel in row))

    def test_no_game_frame(self):
        fb = NHLScreen().render()
        self.assertTrue(any(any(pixel) for row in fb.pixels for pixel in row))

    def test_period_and_clock(self):
        self.assertEqual(status_text(game()), "P3 04:32")

    def test_intermission(self):
        self.assertEqual(status_text(game(clock={"inIntermission": True})), "INT")

    def test_overtime_and_shootout(self):
        self.assertEqual(status_text(game(periodDescriptor={"number": 4, "periodType": "OT"})), "OT 04:32")
        self.assertEqual(status_text(game(gameState="FINAL", periodDescriptor={"number": 5, "periodType": "SO"})), "FINAL SO")

    def test_scheduled_and_postponed(self):
        self.assertEqual(status_text(game(gameState="FUT")), "PREGAME")
        self.assertEqual(status_text(game(gameState="PPD")), "PPD")

    def test_scores_do_not_overlap_labels(self):
        fb = NHLScreen(game()).render()
        self.assertTrue(any(any(pixel) for row in fb.pixels[10:15] for pixel in row[:14]))
        self.assertTrue(any(any(pixel) for row in fb.pixels[10:15] for pixel in row[40:53]))


if __name__ == "__main__":
    unittest.main()
