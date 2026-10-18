"""Offline field coverage checks for the English football contract probe."""
import importlib.util
import io
import json
import unittest
from datetime import date
from pathlib import Path

path = Path(__file__).resolve().parents[1] / "scripts" / "probe-english-contract.py"
spec = importlib.util.spec_from_file_location("english_contract_probe", path)
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)


class EnglishContractProbeTests(unittest.TestCase):
    def test_empty_schedule_is_valid(self):
        self.assertEqual(module.coverage({"events": []})["matches"], 0)

    def test_full_live_fixture(self):
        event = {"id": "12", "date": "2026-10-17T14:00Z",
                 "status": {"type": {"state": "in"}, "displayClock": "45:00"},
                 "competitions": [{"competitors": [
                     {"homeAway": "home", "team": {"id": "1", "name": "A"}, "score": "1"},
                     {"homeAway": "away", "team": {"id": "2", "name": "B"}, "score": "0"}],
                     "details": [{"id": "goal1", "scoringPlay": True}]}]}
        result = module.coverage({"events": [event]})
        self.assertEqual(result, dict(matches=1, kickoff=1, team_ids=1,
                                      team_names=1, status=1, scores=1,
                                      live=1, live_clock=1, scoring_events=1))

    def test_missing_optional_fields_are_reported_not_invented(self):
        event = {"id": "12", "competitions": [{"competitors": [
            {"homeAway": "home"}, {"homeAway": "away"}]}]}
        result = module.coverage({"events": [event]})
        self.assertEqual(result["matches"], 1)
        self.assertEqual(result["scores"], 0)
        self.assertEqual(result["status"], 0)

    def test_missing_competitor_rejected(self):
        with self.assertRaises(ValueError):
            module.coverage({"events": [{"id": "12", "competitions": [
                {"competitors": [{"homeAway": "home"}]}]}]})

    def test_all_four_competitions_are_probed(self):
        urls = []
        def opener(req, timeout):
            urls.append(req.full_url)
            return io.BytesIO(json.dumps({"events": []}).encode())
        rows = module.probe(date(2026, 10, 17), opener=opener)
        self.assertEqual(len(rows), 4)
        self.assertTrue(all(error is None for _, _, error in rows))
        self.assertTrue(all("dates=20261017" in url for url in urls))


if __name__ == "__main__":
    unittest.main()
