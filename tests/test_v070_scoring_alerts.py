"""Tests for cross-sport scoring alert lifecycle and prioritization."""
import unittest

from universal_led.scoring_alerts import ScoreEvent, ScoringAlerts


def event(sport, league, game, eid, team):
    return ScoreEvent(sport, league, game, eid, team, "score")


class ScoringAlertsTests(unittest.TestCase):
    def test_disabled_by_default(self):
        q = ScoringAlerts()
        q.observe("soccer", "EPL", "1", ())
        self.assertEqual(q.observe("soccer", "EPL", "1",
                                   (event("soccer", "EPL", "1", "g1", "ARS"),)), ())
        self.assertIsNone(q.next_alert(0))

    def test_first_snapshot_is_baseline(self):
        q = ScoringAlerts(enabled=True, scope="all")
        goal = event("soccer", "EPL", "1", "g1", "ARS")
        self.assertEqual(q.observe("soccer", "EPL", "1", (goal,)), ())
        self.assertIsNone(q.next_alert(0))
        self.assertEqual(q.observe("soccer", "EPL", "1", (goal,)), ())

    def test_new_event_once_and_expires(self):
        q = ScoringAlerts(enabled=True, scope="all", seconds=5)
        q.observe("soccer", "EPL", "1", ())
        goal = event("soccer", "EPL", "1", "g1", "ARS")
        self.assertEqual(q.observe("soccer", "EPL", "1", (goal,)), (goal,))
        self.assertEqual(q.next_alert(10), goal)
        self.assertEqual(q.next_alert(14), goal)
        self.assertIsNone(q.next_alert(15))
        self.assertEqual(q.observe("soccer", "EPL", "1", ()), ())
        self.assertEqual(q.observe("soccer", "EPL", "1", (goal,)), ())
        self.assertIsNone(q.next_alert(16))

    def test_favorites_scope_excludes_other_teams(self):
        q = ScoringAlerts(enabled=True)
        q.observe("soccer", "EPL", "1", ())
        goal = event("soccer", "EPL", "1", "g1", "ARS")
        self.assertEqual(q.observe("soccer", "EPL", "1", (goal,),
                                   favorite_teams=("MUN",)), ())
        self.assertIsNone(q.next_alert(0))

    def test_favorites_priority_across_sports(self):
        q = ScoringAlerts(enabled=True, scope="all")
        q.observe("soccer", "EPL", "1", ())
        q.observe("baseball", "MLB", "2", ())
        nonfavorite = event("soccer", "EPL", "1", "g1", "ARS")
        favorite = event("baseball", "MLB", "2", "r1", "ATL")
        q.observe("soccer", "EPL", "1", (nonfavorite,), favorite_teams=("MUN",))
        q.observe("baseball", "MLB", "2", (favorite,), favorite_teams=("ATL",))
        self.assertEqual(q.next_alert(0), favorite)
        self.assertEqual(q.next_alert(8), nonfavorite)
        self.assertIsNone(q.next_alert(16))

    def test_disable_clears_pending_and_active(self):
        q = ScoringAlerts(enabled=True, scope="all")
        q.observe("soccer", "EPL", "1", ())
        q.observe("soccer", "EPL", "1", (event("soccer", "EPL", "1", "g1", "ARS"),))
        self.assertIsNotNone(q.next_alert(0))
        q.configure(enabled=False)
        self.assertIsNone(q.next_alert(1))

    def test_rejects_mismatched_game_and_invalid_events(self):
        q = ScoringAlerts(enabled=True, scope="all")
        with self.assertRaises(ValueError):
            q.observe("soccer", "EPL", "1", (event("soccer", "EPL", "2", "g1", "ARS"),))
        with self.assertRaises(ValueError):
            ScoreEvent("soccer", "EPL", "1", "", "ARS", "goal")


if __name__ == "__main__":
    unittest.main()
