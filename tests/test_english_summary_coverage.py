"""Verify ESPN summary diagnostics exercise the real goal adapter."""
import importlib.util
import unittest
from pathlib import Path

SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "probe-english-summary.py"
spec = importlib.util.spec_from_file_location("probe_english_summary", SCRIPT)
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)


class EnglishSummaryCoverageTests(unittest.TestCase):
    def test_scoring_event_is_parsed_and_metadata_counted(self):
        payload = {"keyEvents": [
            {"id": "goal1", "scoringPlay": True,
             "team": {"abbreviation": "ABC"},
             "clock": {"displayValue": "52'"},
             "participants": [{"type": "scorer", "athlete": {"displayName": "Player"}}]},
            {"id": "card1", "scoringPlay": False}]}
        result = module.summary_coverage(payload)
        self.assertEqual(result["key_events_goal_markers"], 1)
        self.assertEqual(result["parsed_goals"], 1)
        self.assertEqual(result["parsed_team_ids"], 1)
        self.assertEqual(result["parsed_scorers"], 1)
        self.assertEqual(result["parsed_minutes"], 1)
        self.assertEqual(result["parsed_unique_ids"], 1)

    def test_missing_optional_fields_are_reported_not_invented(self):
        result = module.summary_coverage({"keyEvents": [
            {"id": "goal1", "scoringPlay": True}]})
        self.assertEqual(result["parsed_goals"], 1)
        self.assertEqual(result["parsed_team_ids"], 0)
        self.assertEqual(result["parsed_scorers"], 0)
        self.assertEqual(result["parsed_minutes"], 0)

    def test_unidentified_goal_is_not_accepted(self):
        result = module.summary_coverage({"keyEvents": [
            {"scoringPlay": True}]})
        self.assertEqual(result["key_events_goal_markers"], 1)
        self.assertEqual(result["parsed_goals"], 0)


if __name__ == "__main__":
    unittest.main()
