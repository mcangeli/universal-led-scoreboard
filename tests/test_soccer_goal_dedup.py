"""Regression coverage for duplicate goal events in a single feed snapshot."""
import unittest

from universal_led.soccer import GoalEventTracker, SoccerGoal, SoccerMatch, new_goals


def match(*goals):
    return SoccerMatch("game-1", "MLS", "ATL", "MIA", 1, 0, "in", tuple(goals))


class SoccerGoalDedupTests(unittest.TestCase):
    def test_tracker_announces_duplicate_event_only_once(self):
        tracker = GoalEventTracker()
        self.assertEqual(tracker.observe(match()), ())
        goal = SoccerGoal("goal-1", "ATL")
        self.assertEqual(tracker.observe(match(goal, goal)), (goal,))
        self.assertEqual(tracker.observe(match(goal)), ())

    def test_new_goals_deduplicates_snapshot(self):
        goal = SoccerGoal("goal-2", "ATL")
        self.assertEqual(new_goals(match(), match(goal, goal)), (goal,))


if __name__ == "__main__":
    unittest.main()
