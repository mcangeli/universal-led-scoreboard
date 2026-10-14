import tempfile
import unittest
from universal_led.mlb_runtime import BackgroundMLBFeed
from universal_led.runtime_settings import ConfiguredMLBRenderer
from universal_led.configurator import HTML

class FakeFeed:
    refresh_seconds=60
    last_error=None
    def games(self):
        return []

class DiagnosticsTests(unittest.TestCase):
    def test_initial_feed_status(self):
        worker=BackgroundMLBFeed(FakeFeed())
        self.assertEqual(worker.status()['state'],'starting')
        self.assertIsNone(worker.status()['last_success'])
    def test_empty_schedule_is_not_fake_matchup(self):
        with tempfile.TemporaryDirectory() as root:
            renderer=ConfiguredMLBRenderer(root,BackgroundMLBFeed(FakeFeed()))
            self.assertIsNone(renderer.game())
            frame=renderer.frame()
            self.assertEqual((frame.width,frame.height),(64,32))
    def test_successful_empty_feed_is_healthy(self):
        worker=BackgroundMLBFeed(FakeFeed())
        worker.refresh_once()
        state=worker.status()
        self.assertEqual(state['state'],'running')
        self.assertEqual(state['games'],0)
        self.assertIsNotNone(state['last_success'])
    def test_diagnostics_on_dashboard(self):
        self.assertIn('last-refresh',HTML)
        self.assertIn('last_success',HTML)

if __name__=='__main__':
    unittest.main()
