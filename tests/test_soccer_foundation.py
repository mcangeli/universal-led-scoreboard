import unittest

from universal_led.soccer import SoccerGoal, SoccerMatch, new_goals


class SoccerFoundationTests(unittest.TestCase):
    def match(self, goals=(), league="MLS", match_id="game-1"):
        return SoccerMatch(match_id, league, "ATL", "MIA", 1, 0, "live", tuple(goals))

    def test_initial_snapshot_does_not_replay_old_goals(self):
        self.assertEqual(new_goals(None, self.match([SoccerGoal("1", "ATL", "Player")])), ())

    def test_new_credited_goal_is_announced_once(self):
        first = self.match()
        goal = SoccerGoal("event-2", "ATL", "Scorer", "67")
        updated = self.match([goal])
        self.assertEqual(new_goals(first, updated), (goal,))
        self.assertEqual(new_goals(updated, updated), ())

    def test_missing_scorer_is_allowed(self):
        goal = SoccerGoal("event-3", "ATL")
        self.assertEqual(new_goals(self.match(), self.match([goal])), (goal,))

    def test_own_goal_metadata_preserved(self):
        goal = SoccerGoal("event-4", "MIA", "Defender", "88", True)
        self.assertTrue(new_goals(self.match(), self.match([goal]))[0].own_goal)

    def test_other_match_not_compared(self):
        self.assertEqual(new_goals(self.match(), self.match([SoccerGoal("2", "ATL")], match_id="game-2")), ())

    def test_nwsl_supported(self):
        goal = SoccerGoal("nwsl-1", "HOME", "Scorer", "12")
        self.assertEqual(new_goals(self.match(league="NWSL"), self.match([goal], league="NWSL")), (goal,))

    def test_unknown_league_rejected(self):
        with self.assertRaises(ValueError):
            new_goals(None, self.match(league="UNKNOWN"))


if __name__ == "__main__":
    unittest.main()
