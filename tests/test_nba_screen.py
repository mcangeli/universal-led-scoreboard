"""NBA renderer regression tests, no hardware or network required."""
import unittest
from datetime import datetime, timezone
from universal_led.nba_data import BasketballGame
from universal_led.nba_screen import NBAScreen, status_text


def game(**changes):
    fields = dict(game_id="401", start_utc=datetime(2026, 10, 17, 0, tzinfo=timezone.utc),
                  away="ATL", home="BOS", away_name="Atlanta Hawks",
                  home_name="Boston Celtics", away_score=123, home_score=119,
                  status="live", period=4, clock="2:31", detail="Q4")
    fields.update(changes)
    return BasketballGame(**fields)


class NBAScreenTests(unittest.TestCase):
    def test_frame_dimensions(self):
        frame = NBAScreen(game()).render()
        self.assertEqual((frame.width, frame.height), (64, 32))

    def test_no_games(self):
        self.assertEqual((NBAScreen().render().width, NBAScreen().render().height), (64, 32))

    def test_live_quarter_and_clock(self):
        self.assertEqual(status_text(game()), "Q4 2:31")

    def test_halftime(self):
        self.assertEqual(status_text(game(detail="Halftime", period=2)), "HALFTIME")

    def test_overtime(self):
        self.assertEqual(status_text(game(period=5, clock="1:09")), "OT 1:09")
        self.assertEqual(status_text(game(period=6, clock="0:22")), "2OT 0:22")

    def test_final_overtime(self):
        self.assertEqual(status_text(game(status="final", period=6)), "FINAL 2OT")

    def test_scheduled_timezone(self):
        self.assertIn("EDT", status_text(game(status="scheduled")))
        self.assertTrue(status_text(game(status="scheduled"), time_format="24h").startswith("20:00"))

    def test_postponed(self):
        self.assertEqual(status_text(game(status="postponed")), "PPD")

    def test_three_digit_scores(self):
        self.assertEqual((game().away_score, game().home_score), (123, 119))
        self.assertEqual((NBAScreen(game()).render().width, NBAScreen(game()).render().height), (64, 32))


if __name__ == "__main__":
    unittest.main()
