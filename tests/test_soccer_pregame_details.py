"""Regression coverage for the shared soccer pregame data and layout."""
import unittest

from universal_led.soccer import SoccerMatch, SUPPORTED_LEAGUES
from universal_led.soccer_feed import parse_scoreboard
from universal_led.soccer_screens import match_screen
from universal_led.soccer_pixels import render_soccer_screen


class SoccerPregameDetailsTests(unittest.TestCase):
    def test_all_six_leagues_render_records_and_kickoff(self):
        for league in sorted(SUPPORTED_LEAGUES):
            with self.subTest(league=league):
                game = SoccerMatch("1", league, "ATL", "MIA", 0, 0, "pre",
                                   kickoff="2026-10-24T23:30:00Z",
                                   home_record="8-10-14", away_record="18-7-7")
                screen = match_screen(game)
                self.assertIn("8-10-14", screen.line2)
                self.assertIn("18-7-7", screen.line1)
                self.assertEqual(screen.footer, "7:30PM")

    def test_full_record_pixels_reach_right_edge_without_clipping(self):
        game = SoccerMatch("1", "MLS", "ATL", "MIA", 0, 0, "pre",
                           home_record="8-10-14", away_record="18-7-7")
        frame = render_soccer_screen(match_screen(game))
        for top in (8, 16):
            self.assertTrue(any(frame.pixels[y][x] != (0, 0, 0)
                                for y in range(top, top + 7) for x in range(0, 18)))
            self.assertTrue(any(frame.pixels[y][x] != (0, 0, 0)
                                for y in range(top, top + 7) for x in range(45, 64)))

    def test_missing_data_is_not_fabricated(self):
        game = SoccerMatch("1", "NWSL", "ATL", "MIA", 0, 0, "pre")
        screen = match_screen(game)
        self.assertIn("--", screen.line1)
        self.assertEqual(screen.footer, "PRE")

    def test_live_scores_not_replaced_by_records(self):
        game = SoccerMatch("1", "MLS", "ATL", "MIA", 2, 1, "in",
                           home_record="8-10-14", away_record="18-7-7")
        screen = match_screen(game)
        self.assertNotIn("8-10-14", screen.line2)
        self.assertIn("2", screen.line2)

    def test_provider_record_and_kickoff_normalized(self):
        def competitor(side, abbreviation, wins, draws, losses):
            return {"homeAway": side, "team": {"id": abbreviation, "abbreviation": abbreviation},
                    "score": "0", "records": [{"stats": [
                        {"name": "wins", "value": wins},
                        {"name": "ties", "value": draws},
                        {"name": "losses", "value": losses}]}]}
        payload = {"events": [{"id": "123", "date": "2026-10-24T23:30Z",
                               "status": {"type": {"state": "pre"}},
                               "competitions": [{"competitors": [
                                   competitor("home", "ATL", 8, 10, 14),
                                   competitor("away", "MIA", 18, 7, 7)]}]}]}
        game, = parse_scoreboard(payload, "MLS")
        self.assertEqual(game.home_record, "8-10-14")
        self.assertEqual(game.away_record, "18-7-7")
        self.assertEqual(match_screen(game).footer, "7:30PM")


if __name__ == "__main__":
    unittest.main()
