"""A cached feed update must not hide subsequently enriched pregame records."""
import unittest
from dataclasses import replace
from universal_led.soccer import SoccerMatch
from universal_led.soccer_display import SoccerDisplayController


class PregameSnapshotTests(unittest.TestCase):
    def test_new_record_survives_older_cached_display_snapshot(self):
        original = SoccerMatch("m", "EPL", "COV", "TOT", 0, 0, "pre")
        controller = SoccerDisplayController()
        controller.update(original)
        enriched = replace(original, home_record="4-2-2", away_record="5-1-2")
        screen = controller.screen(enriched, 0)
        self.assertIn("4-2-2", screen.line1)
        self.assertIn("5-1-2", screen.line2)

    def test_missing_enrichment_does_not_erase_feed_record(self):
        original = SoccerMatch("m", "EPL", "COV", "TOT", 0, 0, "pre",
                               home_record="4-2-2")
        controller = SoccerDisplayController()
        controller.update(original)
        screen = controller.screen(replace(original, home_record=None), 0)
        self.assertIn("4-2-2", screen.line1)


if __name__ == "__main__":
    unittest.main()
