import unittest
from universal_led.nhl_data import parse_game
from universal_led.nhl_visual import NHLVisualScreen, TEAM_COLORS


def fixture(**updates):
    data = {
        "id": 10, "gameState": "LIVE",
        "awayTeam": {"abbrev": "BOS", "score": 12},
        "homeTeam": {"abbrev": "NYR", "score": 3},
        "periodDescriptor": {"number": 3, "periodType": "REG"},
        "clock": {"timeRemaining": "02:15"},
    }
    data.update(updates)
    return parse_game(data)


class NHLVisualTests(unittest.TestCase):
    def test_all_32_team_accents_present(self):
        self.assertEqual(len(TEAM_COLORS), 32)

    def test_native_size_and_pixel_output(self):
        fb = NHLVisualScreen(fixture()).render()
        self.assertEqual((fb.width, fb.height), (64, 32))
        self.assertEqual(len(fb.ppm()), len(b"P6\n64 32\n255\n") + 64 * 32 * 3)

    def test_team_color_visible(self):
        fb = NHLVisualScreen(fixture()).render()
        self.assertIn(TEAM_COLORS["BOS"], fb.pixels[10])

    def test_double_digit_scores(self):
        fb = NHLVisualScreen(fixture()).render()
        self.assertTrue(any(any(p) for row in fb.pixels[10:15] for p in row[50:60]))

    def test_missing_team_color_fallback(self):
        fb = NHLVisualScreen(fixture(awayTeam={"abbrev": "ZZZ"})).render()
        self.assertTrue(any(any(p) for row in fb.pixels[10:15] for p in row[:30]))

    def test_off_day(self):
        fb = NHLVisualScreen().render()
        self.assertTrue(any(any(p) for row in fb.pixels[15:20] for p in row))

    def test_game_states(self):
        for state in ("FUT", "LIVE", "FINAL", "PPD"):
            with self.subTest(state=state):
                fb = NHLVisualScreen(fixture(gameState=state)).render()
                self.assertTrue(any(any(p) for row in fb.pixels for p in row))


if __name__ == "__main__":
    unittest.main()
