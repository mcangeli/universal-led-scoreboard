"""Offline NFL 64x32 renderer tests."""
import unittest
from datetime import datetime, timezone

from universal_led.nfl_data import FootballGame
from universal_led.nfl_screen import NFLScreen, status_text


def game(**changes):
    fields = dict(game_id="401", start_utc=datetime(2026, 10, 18, 17, tzinfo=timezone.utc),
                  away="ATL", home="CHI", away_name="Atlanta Falcons",
                  home_name="Chicago Bears", away_score=17, home_score=14,
                  status="live", period=3, clock="4:32", detail="Q3")
    fields.update(changes)
    return FootballGame(**fields)


class NFLScreenTests(unittest.TestCase):
    def test_frame_dimensions(self):
        frame = NFLScreen(game()).render()
        self.assertEqual((frame.width, frame.height), (64, 32))

    def test_empty_games(self):
        self.assertEqual((NFLScreen().render().width, NFLScreen().render().height), (64, 32))

    def test_live_quarter_clock(self):
        self.assertEqual(status_text(game()), "Q3 4:32")

    def test_halftime(self):
        self.assertEqual(status_text(game(detail="Halftime", period=2)), "HALFTIME")

    def test_overtime(self):
        self.assertEqual(status_text(game(period=5, clock="2:00")), "OT 2:00")

    def test_final_and_postponed(self):
        self.assertEqual(status_text(game(status="final")), "FINAL")
        self.assertEqual(status_text(game(status="postponed")), "PPD")

    def test_pregame_timezone(self):
        self.assertIn("EDT", status_text(game(status="scheduled")))
        self.assertTrue(status_text(game(status="scheduled"), time_format="24h").startswith("13:00"))

    def test_pregame_records_and_scores(self):
        scheduled = game(status="scheduled", away_record="3-2", home_record="4-1")
        self.assertEqual((NFLScreen(scheduled).render().width, NFLScreen(scheduled).render().height), (64, 32))
        self.assertEqual((NFLScreen(game(away_score=105)).render().width, NFLScreen(game(away_score=105)).render().height), (64, 32))


    def test_live_possession_and_down_distance(self):
        active = game(possession="ATL", down=2, distance=7)
        frame = NFLScreen(active).render()
        self.assertEqual((frame.width, frame.height), (64, 32))
        self.assertEqual(frame.pixels[11][20], (245, 175, 60))

    def test_live_without_situation(self):
        frame = NFLScreen(game(possession="", down=None, distance=None)).render()
        self.assertEqual((frame.width, frame.height), (64, 32))

    def test_pregame_ignores_live_situation(self):
        frame = NFLScreen(game(status="scheduled", possession="ATL", down=2, distance=7)).render()
        self.assertEqual((frame.width, frame.height), (64, 32))

if __name__ == "__main__":
    unittest.main()
