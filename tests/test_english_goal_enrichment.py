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
