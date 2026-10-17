import io
import unittest
from datetime import date

from universal_led.soccer_native_http import fetch_native_matches, NativeLeagueProvider
from universal_led.soccer_providers import SoccerProviderRouter


class Response(io.BytesIO):
    def __enter__(self):
        return self
    def __exit__(self, *args):
        self.close()


class NativeHTTPTests(unittest.TestCase):
    day = date(2026, 10, 17)

    def test_mls_https_fetch_and_parse(self):
        calls = []
        def opener(request, timeout):
            calls.append((request.full_url, timeout))
            return Response(b'[{"matchId":"1","homeTeamThreeLetterCode":"ATL","awayTeamThreeLetterCode":"MIA","matchStatus":"Live"}]')
        matches = fetch_native_matches("MLS", self.day,
            url_template="https://league.example/matches?date={date}", opener=opener)
        self.assertEqual(matches[0].league, "MLS")
        self.assertEqual(calls, [("https://league.example/matches?date=20261017", 5.0)])

    def test_nwsl_https_fetch_and_parse(self):
        def opener(request, timeout):
            return Response(b'[{"match_id":"1","home_team_id":"ATL","away_team_id":"BOS","status":"Live"}]')
        matches = fetch_native_matches("NWSL", self.day,
            url_template="https://league.example/matches", opener=opener)
        self.assertEqual(matches[0].league, "NWSL")

    def test_http_rejected(self):
        with self.assertRaises(ValueError):
            fetch_native_matches("MLS", self.day, url_template="http://league.example/matches")

    def test_embedded_credentials_rejected(self):
        with self.assertRaises(ValueError):
            fetch_native_matches("MLS", self.day, url_template="https://user:pass@league.example/")

    def test_missing_endpoint_rejected(self):
        with self.assertRaises(ValueError):
            fetch_native_matches("MLS", self.day, url_template="")

    def test_invalid_timeout_rejected(self):
        with self.assertRaises(ValueError):
            fetch_native_matches("MLS", self.day, url_template="https://league.example", timeout=0)

    def test_invalid_headers_rejected(self):
        with self.assertRaises(ValueError):
            fetch_native_matches("MLS", self.day, url_template="https://league.example",
                                 headers={"Authorization": "bad\r\nHeader: injected"})

    def test_invalid_native_payload_rejected(self):
        def opener(request, timeout):
            return Response(b'{"unrecognized":[]}')
        with self.assertRaises(ValueError):
            fetch_native_matches("MLS", self.day,
                                 url_template="https://league.example/matches", opener=opener)

    def test_native_provider_works_with_router(self):
        def opener(request, timeout):
            return Response(b'[{"matchId":"1","homeTeamThreeLetterCode":"ATL","awayTeamThreeLetterCode":"MIA","matchStatus":"Live"}]')
        primary = NativeLeagueProvider("MLS", url_template="https://league.example/matches", opener=opener)
        router = SoccerProviderRouter("MLS", primary=primary,
                                      fallback=lambda day: self.fail("Fallback called"))
        self.assertEqual(router.fetch(self.day)[0].home_id, "ATL")
        self.assertEqual(router.last_source, "league")


if __name__ == "__main__":
    unittest.main()
