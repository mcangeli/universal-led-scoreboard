import unittest

from universal_led.soccer import SoccerGoal, SoccerMatch
from universal_led.soccer_screens import goal_screen, match_screen


class SoccerScreenTests(unittest.TestCase):
    def match(self, league="MLS"):
        return SoccerMatch("m1", league, "ATL", "MIA", 2, 1, "live")

    def test_match_screen_has_scores_and_league(self):
        screen = match_screen(self.match())
        self.assertEqual(screen.kind, "match")
        self.assertEqual(screen.header, "MLS")
        self.assertIn("MIA", screen.line1)
        self.assertIn("ATL", screen.line2)
        self.assertIn("2", screen.line2)

    def test_live_match_shows_half_and_clock(self):
        game = SoccerMatch("m1", "MLS", "ATL", "MIA", 2, 1, "in", clock="67'", period=2)
        self.assertEqual(match_screen(game).footer, "2H 67'")

    def test_live_without_clock_shows_live(self):
        game = SoccerMatch("m1", "MLS", "ATL", "MIA", 2, 1, "in")
        self.assertEqual(match_screen(game).footer, "LIVE")

    def test_final_shows_final(self):
        game = SoccerMatch("m1", "NWSL", "ATL", "MIA", 2, 1, "post")
        self.assertEqual(match_screen(game).footer, "FINAL")

    def test_stoppage_time_preserved(self):
        game = SoccerMatch("m1", "MLS", "ATL", "MIA", 2, 1, "in", clock="90+3'", period=2)
        self.assertEqual(match_screen(game).footer, "2H 90+3'")

    def test_nwsl_match_uses_shared_layout(self):
        self.assertEqual(match_screen(self.match("NWSL")).header, "NWSL")

    def test_credited_scorer_is_displayed(self):
        screen = goal_screen(self.match(), SoccerGoal("g1", "ATL", "Alex Forward", "67'"))
        self.assertEqual(screen.header, "GOAL!")
        self.assertEqual(screen.line1, "Alex Forward")
        self.assertIn("67'", screen.line2)

    def test_missing_scorer_falls_back_to_team(self):
        screen = goal_screen(self.match(), SoccerGoal("g2", "MIA"))
        self.assertEqual(screen.line1, "MIA")

    def test_own_goal_is_labeled(self):
        screen = goal_screen(self.match(), SoccerGoal("g3", "ATL", "Defender", "81'", True))
        self.assertEqual(screen.header, "OWN GOAL")

    def test_long_scorer_is_bounded(self):
        screen = goal_screen(self.match(), SoccerGoal("g4", "ATL", "Extremely Long Player Name"))
        self.assertLessEqual(len(screen.line1), 16)

    def test_score_is_present_on_goal_screen(self):
        screen = goal_screen(self.match("NWSL"), SoccerGoal("g5", "ATL"))
        self.assertIn("1-2", screen.footer)
        self.assertIn("NWSL", screen.footer)


if __name__ == "__main__":
    unittest.main()
