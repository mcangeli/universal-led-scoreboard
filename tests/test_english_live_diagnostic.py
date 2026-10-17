"""Offline checks for read-only live English football diagnostic."""
import importlib.util
import io
import json
import unittest
from datetime import date
from pathlib import Path

SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "diagnose-english-live.py"
spec = importlib.util.spec_from_file_location("diagnose_english_live", SCRIPT)
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)


def fixture(state="in", clock=None, details=()):
    status = {"type": {"state": state}}
    if clock is not None:
        status["displayClock"] = clock
    return {"events": [{"id": "123", "status": status, "competitions": [{
        "competitors": [
            {"homeAway": "home", "team": {"id": "1", "abbreviation": "H"}, "score": "2"},
            {"homeAway": "away", "team": {"id": "2", "abbreviation": "A"}, "score": "1"}],
        "details": list(details)}]}]}


class EnglishLiveDiagnosticTests(unittest.TestCase):
    def test_empty_day_does_not_claim_live_support(self):
        result = module.inspect({"events": []}, "EPL")
        self.assertEqual(result["live"], 0)
        self.assertEqual(result["live_clocks"], 0)

    def test_live_clock_without_goal_events(self):
        result = module.inspect(fixture(clock="67:20"), "LEAGUE_ONE")
        self.assertEqual(result["live"], 1)
        self.assertEqual(result["live_clocks"], 1)
        self.assertEqual(result["live_goal_events"], 0)

    def test_live_goal_id_is_counted_only_if_present(self):
        goal = {"id": "g1", "scoringPlay": True, "team": {"abbreviation": "H"}}
        result = module.inspect(fixture(clock="78:00", details=[goal]), "CHAMPIONSHIP")
        self.assertEqual(result["live_goal_ids"], 1)

    def test_completed_match_reports_historical_goals_without_claiming_live_delivery(self):
        goal = {"id": "goal-1", "scoringPlay": True, "team": {"abbreviation": "H"}}
        result = module.inspect(fixture(state="post", details=[goal]), "EPL")
        self.assertEqual(result["live"], 0)
        self.assertEqual(result["live_goal_events"], 0)
        self.assertEqual(result["final"], 1)
        self.assertEqual(result["final_goal_events"], 1)
        self.assertEqual(result["final_goal_ids"], 1)
        self.assertEqual(result["final_with_goals"], 1)

    def test_completed_match_without_details_does_not_invent_goals(self):
        result = module.inspect(fixture(state="post"), "LEAGUE_TWO")
        self.assertEqual(result["final"], 1)
        self.assertEqual(result["final_goal_events"], 0)

    def test_probe_uses_all_four_divisions(self):
        urls = []
        def opener(request, timeout):
            urls.append(request.full_url)
            return io.BytesIO(json.dumps({"events": []}).encode())
        results = module.probe(date(2026, 10, 17), opener=opener)
        self.assertEqual(len(results), 4)
        self.assertTrue(all("coverage" in value for value in results.values()))
        self.assertEqual(len(set(urls)), 4)


if __name__ == "__main__":
    unittest.main()
