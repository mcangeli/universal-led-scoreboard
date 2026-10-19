"""Pregame standings caches are independent of optional standings pages."""
import unittest
from types import SimpleNamespace
from universal_led.multisport_runtime import MultiSportRenderer


class Adapter:
    def __init__(self):
        self.caches = None
    def set_standings_caches(self, caches):
        self.caches = caches


class IndependentPregameCacheTests(unittest.TestCase):
    def test_english_cache_without_standings_rotation(self):
        english = Adapter()
        cache = SimpleNamespace(rows=lambda: (1,), status=lambda: {"error": None})
        board = MultiSportRenderer(None, None, english_renderer=english,
                                   soccer_standings_caches={"EPL": cache})
        self.assertIs(english.caches["EPL"], cache)
        self.assertEqual(board.soccer_pregame_diagnostics()["EPL"]["teams"], 1)

    def test_late_cache_attachment_without_idle_pages(self):
        english = Adapter()
        board = MultiSportRenderer(None, None, english_renderer=english)
        cache = SimpleNamespace(rows=lambda: (), status=lambda: {"error": "offline"})
        board.set_soccer_standings_caches({"EPL": cache})
        self.assertIs(english.caches["EPL"], cache)
        self.assertEqual(board.soccer_pregame_diagnostics()["EPL"]["state"], "error")


if __name__ == "__main__":
    unittest.main()
