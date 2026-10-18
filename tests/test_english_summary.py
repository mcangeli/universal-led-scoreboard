"""Contract tests for ESPN English football match-summary goals."""
import unittest
from universal_led.english_summary import parse_key_event_goals


class EnglishSummaryGoalTests(unittest.TestCase):
    def test_goal_with_official_id_team_and_minute(self):
        data = {"keyEvents": [{"id": "g-1", "scoringPlay": True,
                               "team": {"abbreviation": "ARS"},
                               "clock": {"displayValue": "72'"},
                               "participants": [{"type": "scorer",
                                                 "athlete": {"displayName": "Player A"}}]}]}
        goals = parse_key_event_goals(data)
        self.assertEqual(len(goals), 1)
        self.assertEqual((goals[0].event_id, goals[0].team_id, goals[0].minute),
                         ("g-1", "ARS", "72'"))
        self.assertEqual(goals[0].scorer, "Player A")

    def test_cards_and_substitutions_are_not_goals(self):
        self.assertEqual(parse_key_event_goals({"keyEvents": [
            {"id": "card", "scoringPlay": False, "type": {"text": "Yellow Card"}},
            {"id": "sub", "type": {"text": "Substitution"}}]}), ())

    def test_missing_ids_are_not_fabricated(self):
        self.assertEqual(parse_key_event_goals({"keyEvents": [
            {"scoringPlay": True, "team": {"id": "42"}}]}), ())

    def test_duplicate_goal_ids_are_deduplicated(self):
        data = {"keyEvents": [{"id": "1", "scoringPlay": True},
                              {"id": "1", "scoringPlay": True}]}
        self.assertEqual(len(parse_key_event_goals(data)), 1)

    def test_unknown_participant_role_does_not_invent_scorer(self):
        data = {"keyEvents": [{"id": "1", "scoringPlay": True,
                               "participants": [{"athlete": {"displayName": "Assistant"}}]}]}
        self.assertIsNone(parse_key_event_goals(data)[0].scorer)

    def test_non_list_key_events_and_invalid_payload(self):
        self.assertEqual(parse_key_event_goals({"keyEvents": {}}), ())
        with self.assertRaises(ValueError):
            parse_key_event_goals(None)


if __name__ == "__main__":
    unittest.main()
