"""NFL standings feed contracts: divisions, records, validation and HTTP headers."""
import io
import json
import unittest

from universal_led.nfl_standings_feed import (
    NFL_STANDINGS_URL, fetch_nfl_division, fetch_nfl_standings,
    parse_nfl_standings,
)


def entry(code, wins, losses, ties):
    return {"team": {"id": code, "abbreviation": code},
            "stats": [{"name": key, "value": value} for key, value in (
                ("wins", wins), ("losses", losses), ("ties", ties))]}


def fixture():
    return {"children": [
        {"children": [
            {"name": "AFC East", "standings": {"entries": [
                entry("BUF", 5, 1, 0), entry("NE", 4, 2, 0)]}},
            {"name": "AFC North", "standings": {"entries": [
                entry("BAL", 3, 2, 1)]}}]},
        {"children": [{"name": "NFC South", "standings": {"entries": [
            entry("ATL", 3, 3, 0)]}}]},
    ]}


class NFLStandingsFeedTests(unittest.TestCase):
    def test_division_order_and_ties(self):
        rows = parse_nfl_standings(fixture())
        self.assertEqual([(r.group, r.abbreviation, r.rank) for r in rows],
                         [("AFC East", "BUF", 1), ("AFC East", "NE", 2),
                          ("AFC North", "BAL", 1), ("NFC South", "ATL", 1)])
        self.assertEqual((rows[2].played, rows[2].wins, rows[2].losses,
                          rows[2].draws), (6, 3, 2, 1))
        self.assertEqual([r.abbreviation for r in fetch_nfl_division(
            "AFC East", fetcher=lambda _: rows)], ["BUF", "NE"])

    def test_reject_unknown_division_and_bad_payload(self):
        with self.assertRaises(ValueError):
            fetch_nfl_division("AFC Space", fetcher=lambda _: ())
        with self.assertRaises(ValueError):
            parse_nfl_standings([])
        with self.assertRaises(ValueError):
            parse_nfl_standings({"children": None})

    def test_skip_incomplete_records(self):
        payload = fixture()
        payload["children"][0]["children"][0]["standings"]["entries"].append(
            {"team": {"abbreviation": "NYJ"}, "stats": []})
        self.assertEqual(len(parse_nfl_standings(payload)), 4)

    def test_fetch_uses_request_headers(self):
        calls = []

        class Response(io.BytesIO):
            def __enter__(self):
                return self

            def __exit__(self, *args):
                self.close()

        def opener(request, *, timeout):
            calls.append((request, timeout))
            return Response(json.dumps(fixture()).encode())

        rows = fetch_nfl_standings(opener=opener)
        self.assertEqual(len(rows), 4)
        self.assertEqual(len(calls), 1)
        request, timeout = calls[0]
        self.assertEqual(request.full_url, NFL_STANDINGS_URL)
        self.assertEqual(timeout, 12)
        self.assertEqual(request.get_header("Accept"), "application/json")
        self.assertIn("UniversalLEDScoreboard", request.get_header("User-agent"))


if __name__ == "__main__":
    unittest.main()
