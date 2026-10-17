import unittest

from universal_led.soccer import SoccerGoal, SoccerMatch
from universal_led.soccer_display import SoccerDisplayController


class SoccerDisplayTests(unittest.TestCase):
    def match(self, goals=(), league="MLS", match_id="m1"):
        return SoccerMatch(match_id, league, "ATL", "MIA", 2, 1, "live", tuple(goals))

    def test_initial_snapshot_does_not_celebrate(self):
        controller = SoccerDisplayController()
        match = self.match([SoccerGoal("old", "ATL", "Old Scorer")])
        controller.update(match)
        self.assertEqual(controller.screen(match, 0).kind, "match")

    def test_new_goal_interrupts_then_expires(self):
        controller = SoccerDisplayController(goal_seconds=8)
        first = self.match()
        controller.update(first)
        goal = SoccerGoal("new", "ATL", "Alex Forward", "67'")
        updated = self.match([goal])
        controller.update(updated)
        self.assertEqual(controller.screen(updated, 100).kind, "goal")
        self.assertEqual(controller.screen(updated, 107.9).kind, "goal")
        self.assertEqual(controller.screen(updated, 108).kind, "match")

    def test_refresh_does_not_restart_timer(self):
        controller = SoccerDisplayController(goal_seconds=8)
        first = self.match()
        controller.update(first)
        current = self.match([SoccerGoal("g1", "ATL")])
        controller.update(current)
        controller.screen(current, 10)
        controller.update(current)
        self.assertEqual(controller.screen(current, 18).kind, "match")

    def test_goal_duration_is_configurable(self):
        controller = SoccerDisplayController(goal_seconds=3)
        first = self.match()
        controller.update(first)
        updated = self.match([SoccerGoal("g1", "ATL")])
        controller.update(updated)
        self.assertEqual(controller.screen(updated, 10).kind, "goal")
        self.assertEqual(controller.screen(updated, 13).kind, "match")

    def test_late_goal_correction_after_final_does_not_celebrate(self):
        controller = SoccerDisplayController()
        first = self.match()
        controller.update(first)
        final = SoccerMatch("m1", "MLS", "ATL", "MIA", 2, 1, "post",
                            (SoccerGoal("late", "ATL"),))
        controller.update(final)
        self.assertEqual(controller.screen(final, 10).kind, "match")

    def test_final_status_clears_queued_goal(self):
        controller = SoccerDisplayController()
        first = self.match()
        controller.update(first)
        updated = self.match([SoccerGoal("g1", "ATL")])
        controller.update(updated)
        final = SoccerMatch("m1", "MLS", "ATL", "MIA", 2, 1, "post", updated.goals)
        controller.update(final)
        self.assertEqual(controller.screen(final, 10).kind, "match")

    def test_final_status_stops_active_goal_screen(self):
        controller = SoccerDisplayController()
        first = self.match()
        controller.update(first)
        updated = self.match([SoccerGoal("g1", "ATL")])
        controller.update(updated)
        self.assertEqual(controller.screen(updated, 10).kind, "goal")
        final = SoccerMatch("m1", "MLS", "ATL", "MIA", 2, 1, "post", updated.goals)
        controller.update(final)
        self.assertEqual(controller.screen(final, 11).kind, "match")

    def test_halftime_late_goal_does_not_celebrate(self):
        controller = SoccerDisplayController()
        first = self.match()
        controller.update(first)
        halftime = SoccerMatch("m1", "MLS", "ATL", "MIA", 2, 1, "halftime",
                               (SoccerGoal("late", "ATL"),))
        controller.update(halftime)
        self.assertEqual(controller.screen(halftime, 10).footer, "HT")

    def test_halftime_clears_queued_goal_and_keeps_ht(self):
        controller = SoccerDisplayController()
        first = self.match()
        controller.update(first)
        updated = self.match([SoccerGoal("g1", "ATL")])
        controller.update(updated)
        halftime = SoccerMatch("m1", "MLS", "ATL", "MIA", 2, 1, "halftime", updated.goals)
        controller.update(halftime)
        self.assertEqual(controller.screen(halftime, 10).footer, "HT")

    def test_invalid_duration_rejected(self):
        with self.assertRaises(ValueError):
            SoccerDisplayController(goal_seconds=0)

    def test_goal_does_not_appear_on_other_match(self):
        controller = SoccerDisplayController()
        first = self.match()
        other = self.match(league="NWSL")
        controller.update(first)
        controller.update(other)
        updated = self.match([SoccerGoal("g1", "ATL")])
        controller.update(updated)
        self.assertEqual(controller.screen(other, 20).kind, "match")
        self.assertEqual(controller.screen(updated, 20).kind, "goal")

    def test_multiple_goals_are_queued(self):
        controller = SoccerDisplayController(goal_seconds=2)
        first = self.match()
        controller.update(first)
        updated = self.match([SoccerGoal("g1", "ATL", "First"), SoccerGoal("g2", "MIA", "Second")])
        controller.update(updated)
        self.assertEqual(controller.screen(updated, 10).line1, "First")
        self.assertEqual(controller.screen(updated, 12).line1, "Second")
        self.assertEqual(controller.screen(updated, 14).kind, "match")


if __name__ == "__main__":
    unittest.main()
