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
