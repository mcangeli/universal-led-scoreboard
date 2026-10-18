"""End-to-end simulated English live goal delivery and rotation acceptance."""
import unittest
from datetime import date

from universal_led.english_goals import EnglishGoalEnricher
from universal_led.english_rotation import EnglishFootballRenderer
from universal_led.soccer_data import SoccerFeed


def scoreboard(state, score, clock=""):
    return {"events": [{"id": "401", "status": {
        "type": {"state": state, "name": "STATUS_IN_PROGRESS" if state == "in" else
                 "STATUS_FINAL" if state == "post" else "STATUS_SCHEDULED"},
        "displayClock": clock, "period": 2},
        "competitions": [{"competitors": [
            {"homeAway": "home", "team": {"id": "100", "abbreviation": "HOME"}, "score": str(score)},
            {"homeAway": "away", "team": {"id": "101", "abbreviation": "AWAY"}, "score": "0"}]}]}]}


class EnglishSimulatedLiveAcceptance(unittest.TestCase):
    def test_new_goal_once_and_final_does_not_fetch(self):
        snapshots = [scoreboard("pre", 0), scoreboard("in", 0, "51:00"),
                     scoreboard("in", 1, "52:00"), scoreboard("in", 1, "53:00"),
                     scoreboard("post", 1)]
        calls = []
        summary = {"keyEvents": []}
        def scores(*args):
            return snapshots.pop(0)
        def goals(*args):
            calls.append(args)
            return summary
        feed = SoccerFeed("EPL", fetcher=scores, enrich=EnglishGoalEnricher(fetcher=goals))
        renderer = EnglishFootballRenderer({"EPL": feed}, enabled=("EPL",), clock=lambda: 10.0)
        day = date(2026, 10, 17)
        first = feed.refresh(day, force=True)[0]
        renderer.update(first)
        self.assertFalse(renderer.has_live_games())
        second = feed.refresh(day, force=True)[0]
        renderer.update(second)
        self.assertTrue(renderer.has_live_games())
        self.assertEqual(renderer.display.screen(second, 10).kind, "match")
        summary["keyEvents"] = [{"id": "official-goal-1", "scoringPlay": True,
                                 "team": {"abbreviation": "HOME"},
                                 "clock": {"displayValue": "52'"},
                                 "participants": [{"athlete": {"displayName": "Scorer"}}]}]
        third = feed.refresh(day, force=True)[0]
        renderer.update(third)
        self.assertEqual(third.goals[0].scorer, "Scorer")
        self.assertEqual(renderer.display.screen(third, 11).kind, "goal")
        fourth = feed.refresh(day, force=True)[0]
        renderer.update(fourth)
        self.assertEqual(renderer.display.screen(fourth, 20).kind, "match")
        final = feed.refresh(day, force=True)[0]
        renderer.update(final)
        self.assertFalse(renderer.has_live_games())
        self.assertEqual(len(calls), 3)

    def test_summary_outage_keeps_live_scores(self):
        def outage(*args):
            raise OSError("summary unavailable")
        feed = SoccerFeed("EPL", fetcher=lambda *args: scoreboard("in", 2, "65:00"),
                          enrich=EnglishGoalEnricher(fetcher=outage))
        match = feed.refresh(date(2026, 10, 17))[0]
        self.assertEqual(match.home_score, 2)
        self.assertEqual(match.goals, ())


if __name__ == "__main__":
    unittest.main()
