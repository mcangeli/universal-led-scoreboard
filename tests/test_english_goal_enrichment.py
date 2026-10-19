"""English ESPN summary enrichment acceptance tests (offline)."""
import unittest
from datetime import date

from universal_led.english_goals import EnglishGoalEnricher
from universal_led.soccer import SoccerMatch
from universal_led.soccer_data import SoccerFeed


def match(status="in"):
    return SoccerMatch(match_id="123", league="EPL", home_id="ARS", away_id="CHE",
                       home_score=1, away_score=0, status=status)


class EnglishGoalEnrichmentTests(unittest.TestCase):
    def test_live_summary_goals_attached(self):
        enricher = EnglishGoalEnricher(fetcher=lambda league, mid: {"keyEvents": [
            {"id": "goal1", "scoringPlay": True, "team": {"abbreviation": "ARS"},
             "participants": [{"athlete": {"displayName": "Player"}}]}]})
        enriched = enricher(match())
        self.assertEqual(enriched.goals[0].event_id, "goal1")
        self.assertEqual(enriched.goals[0].scorer, "Player")

    def test_scheduled_and_final_never_fetch_summaries(self):
        def forbidden(*args):
            raise AssertionError("unexpected network fetch")
        enricher = EnglishGoalEnricher(fetcher=forbidden)
        self.assertEqual(enricher(match("pre")).goals, ())
        self.assertEqual(enricher(match("post")).goals, ())

    def test_summary_failure_preserves_scoreboard(self):
        def failing(*args):
            raise OSError("offline")
        original = match()
        self.assertEqual(EnglishGoalEnricher(fetcher=failing)(original), original)

    def test_temporary_summary_outage_retains_confirmed_goals(self):
        from universal_led.soccer import GoalEventTracker
        responses = [
            {"keyEvents": [{"id": "g1", "scoringPlay": True}]},
            OSError("temporary outage"),
            {"keyEvents": [{"id": "g1", "scoringPlay": True}]},
        ]
        def fetch(*args):
            response = responses.pop(0)
            if isinstance(response, Exception):
                raise response
            return response
        enricher = EnglishGoalEnricher(fetcher=fetch)
        tracker = GoalEventTracker()
        initial = enricher(match())
        self.assertEqual(tracker.observe(initial), ())
        during_outage = enricher(match())
        self.assertEqual([goal.event_id for goal in during_outage.goals], ["g1"])
        self.assertEqual(tracker.observe(during_outage), ())
        recovered = enricher(match())
        self.assertEqual(tracker.observe(recovered), ())

    def test_empty_summary_does_not_erase_scoreboard_goal(self):
        from dataclasses import replace
        from universal_led.soccer import SoccerGoal
        enricher = EnglishGoalEnricher(fetcher=lambda *args: {"keyEvents": []})
        observed = replace(match(), goals=(SoccerGoal("scoreboard-1", "ARS"),))
        self.assertEqual(enricher(observed).goals[0].event_id, "scoreboard-1")
        self.assertEqual(enricher(match()).goals[0].event_id, "scoreboard-1")

    def test_late_summary_enriches_without_losing_prior_goal(self):
        from dataclasses import replace
        from universal_led.soccer import SoccerGoal
        responses = [{"keyEvents": []}, {"keyEvents": [
            {"id": "summary-2", "scoringPlay": True,
             "team": {"abbreviation": "CHE"}}]}]
        enricher = EnglishGoalEnricher(fetcher=lambda *args: responses.pop(0))
        observed = replace(match(), goals=(SoccerGoal("scoreboard-1", "ARS"),))
        enricher(observed)
        enriched = enricher(match())
        self.assertEqual({g.event_id for g in enriched.goals},
                         {"scoreboard-1", "summary-2"})

    def test_goal_cache_isolated_per_match(self):
        enricher = EnglishGoalEnricher(fetcher=lambda *args: {
            "keyEvents": [{"id": "g1", "scoringPlay": True}]})
        enricher(match())
        from dataclasses import replace
        other = replace(match(), match_id="different")
        enricher.fetcher = lambda *args: (_ for _ in ()).throw(OSError("offline"))
        self.assertEqual(enricher(other).goals, ())
        self.assertEqual(enricher(match()).goals[0].event_id, "g1")

    def test_feed_refresh_runs_enrichment_and_retains_scores(self):
        enricher = EnglishGoalEnricher(fetcher=lambda *args: {"keyEvents": [
            {"id": "goal1", "scoringPlay": True}]})
        payload = {"events": [{"id": "123", "status": {"type": {"state": "in"}},
                               "competitions": [{"competitors": [
                                   {"homeAway": "home", "team": {"abbreviation": "ARS"}, "score": "1"},
                                   {"homeAway": "away", "team": {"abbreviation": "CHE"}, "score": "0"}]}]}]}
        feed = SoccerFeed("EPL", fetcher=lambda *args: payload, enrich=enricher)
        games = feed.refresh(date(2026, 10, 17))
        self.assertEqual(games[0].home_score, 1)
        self.assertEqual(games[0].goals[0].event_id, "goal1")


if __name__ == "__main__":
    unittest.main()
