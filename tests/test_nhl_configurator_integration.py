"""Regression checks for the shared frame publisher integration."""
import inspect
import unittest
from universal_led import configurator


class NHLConfiguratorIntegrationTests(unittest.TestCase):
    def test_shared_frame_router_used_by_publisher_and_preview(self):
        source = inspect.getsource(configurator.main)
        # Verify the shared publisher and routing, not the precise constructor spelling.
        self.assertIn("board = MultiSportRenderer(", source)
        self.assertIn("write_frame(frame_path, board.frame())", source)
        self.assertIn("feed_status,board.frame,countdown_status", source)
        self.assertIn("nba_renderer = ConfiguredNBARenderer(nba_feed)", source)
        self.assertIn("nfl_renderer = ConfiguredNFLRenderer(nfl_feed)", source)
        self.assertIn("nfl_feed.stop()", source)
        self.assertIn("write_frame(frame_path, board.frame())", source)
        self.assertIn("feed_status,board.frame,countdown_status", source)

    def test_mlb_remains_default(self):
        from universal_led.multisport_runtime import MultiSportRenderer
        class Renderer:
            def frame(self):
                return "baseball"
            def game(self):
                return None
        board = MultiSportRenderer(Renderer(), Renderer())
        self.assertEqual(board.active_sport, "mlb")
        self.assertEqual(board.frame(), "baseball")


if __name__ == "__main__":
    unittest.main()
