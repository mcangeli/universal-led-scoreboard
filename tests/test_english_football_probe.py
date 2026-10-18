"""Offline regression tests for the four-division ESPN validation probe."""
import importlib.util
import io
import json
import unittest
from pathlib import Path
from urllib.error import URLError

PATH = Path(__file__).resolve().parents[1] / "scripts" / "probe-english-football.py"
spec = importlib.util.spec_from_file_location("english_football_probe", PATH)
probe = importlib.util.module_from_spec(spec)
spec.loader.exec_module(probe)


class Response(io.BytesIO):
    def __enter__(self):
        return self

    def __exit__(self, *args):
        self.close()


class EnglishFootballProbeTests(unittest.TestCase):
    def test_four_distinct_divisions(self):
        self.assertEqual(list(probe.LEAGUES.values()), ["eng.1", "eng.2", "eng.3", "eng.4"])

    def test_empty_is_not_an_error(self):
        self.assertEqual(probe.inspect_payload({"events": []}), ("EMPTY", 0, 0))

    def test_valid_fixture(self):
        fixture = {"events": [{"id": "123", "competitions": [{
            "competitors": [{"homeAway": "home"}, {"homeAway": "away"}]
        }]}]}
        self.assertEqual(probe.inspect_payload(fixture), ("OK", 1, 1))

    def test_malformed_fixture_rejected(self):
        with self.assertRaises(ValueError):
            probe.inspect_payload({"events": [{"id": "123", "competitions": []}]})

    def test_missing_events_rejected(self):
        with self.assertRaises(ValueError):
            probe.inspect_payload({"league": {}})

    def test_all_four_requests_and_results(self):
        urls = []
        def opener(req, timeout):
            urls.append(req.full_url)
            return Response(json.dumps({"events": []}).encode())
        rows = probe.probe(__import__("datetime").date(2026, 10, 17), opener=opener)
        self.assertEqual(len(rows), 4)
        self.assertTrue(all(row[2] == "EMPTY" for row in rows))
        self.assertTrue(all("dates=20261017" in url for url in urls))

    def test_one_failure_does_not_skip_remaining_divisions(self):
        def opener(req, timeout):
            if "/eng.3/" in req.full_url:
                raise URLError("offline")
            return Response(b'{"events":[]}')
        rows = probe.probe(__import__("datetime").date(2026, 10, 17), opener=opener)
        self.assertEqual([row[2] for row in rows], ["EMPTY", "EMPTY", "ERROR", "EMPTY"])


if __name__ == "__main__":
    unittest.main()
