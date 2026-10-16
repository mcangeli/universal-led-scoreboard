"""Verify NHL API requests identify the client and request JSON."""
import io
import unittest
from datetime import date
from unittest.mock import patch

from universal_led.nhl_feed import fetch_scores


class NHLRequestTests(unittest.TestCase):
    def test_request_headers_and_date(self):
        captured = {}
        def fake_open(request, timeout):
            captured["request"] = request
            captured["timeout"] = timeout
            return io.BytesIO(b'{"games":[]}')
        with patch("universal_led.nhl_feed.urlopen", side_effect=fake_open):
            self.assertEqual(fetch_scores(date(2026, 10, 16)), {"games": []})
        self.assertIn("/2026-10-16", captured["request"].full_url)
        self.assertIn("UniversalLEDScoreboard", captured["request"].get_header("User-agent"))
        self.assertEqual(captured["request"].get_header("Accept"), "application/json")


if __name__ == "__main__":
    unittest.main()
