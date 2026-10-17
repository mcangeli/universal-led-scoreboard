"""Guard the production service wiring for English football.

These checks deliberately avoid starting HTTP servers or contacting ESPN.
"""
import unittest
from pathlib import Path
from unittest.mock import patch

from universal_led.english_football import COMPETITIONS
from universal_led.english_rotation import EnglishFootballRenderer
from universal_led.soccer_data import SoccerFeed
from universal_led.soccer_runtime import BackgroundSoccerFeed
from universal_led.sport_settings import DEFAULT_SETTINGS, validate_settings


class EnglishServiceWiringTests(unittest.TestCase):
    def test_four_distinct_cached_feeds(self):
        feeds = {league: SoccerFeed(league) for league in COMPETITIONS}
        self.assertEqual(set(feeds), set(COMPETITIONS))
        self.assertEqual({feed.league for feed in feeds.values()}, set(COMPETITIONS))

    def test_workers_forward_to_shared_renderer(self):
        feeds = {league: SoccerFeed(league) for league in COMPETITIONS}
        renderer = EnglishFootballRenderer(feeds)
        workers = {league: BackgroundSoccerFeed(feed, on_match=renderer.update)
                   for league, feed in feeds.items()}
        self.assertEqual(len(workers), 4)
        self.assertTrue(all(worker.on_match == renderer.update for worker in workers.values()))

    def test_default_config_cannot_start_english_polling(self):
        settings = validate_settings(DEFAULT_SETTINGS)
        self.assertFalse(settings["sports"]["english"]["enabled"])

    def test_configurator_includes_runtime_wiring(self):
        source = Path(__file__).resolve().parents[1] / "universal_led" / "configurator.py"
        text = source.read_text(encoding="utf-8")
        self.assertIn("english_renderer=english_renderer", text)
        self.assertIn("english_workers.values()", text)
        self.assertIn("sport_enabled=settings['sports']['english']['enabled']", text)
        self.assertIn("sync_english_workers(", text)


if __name__ == "__main__":
    unittest.main()
