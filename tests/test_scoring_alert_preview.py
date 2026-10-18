"""Board preview and live scoring interruption share one frame format."""
import unittest
from universal_led.display import Framebuffer
from universal_led.scoring_alerts import ScoringAlerts, ScoreEvent
from universal_led.multisport_runtime import MultiSportRenderer
from universal_led.web_preview import frame_payload


class PreviewScoringAlertTests(unittest.TestCase):
    def test_frame_payload_matches_matrix_dimensions(self):
        frame = Framebuffer(64, 32)
        payload = frame_payload(frame)
        self.assertEqual((payload['width'], payload['height']), (64, 32))
        self.assertEqual(len(payload['pixels']), 2048)

    def test_preview_follows_alert_and_returns_to_normal_frame(self):
        class Renderer:
            def frame(self):
                return Framebuffer(64, 32)
        now = [0]
        alerts = ScoringAlerts(enabled=True, scope='all', seconds=2)
        event = ScoreEvent('soccer', 'EPL', '1', 'goal-1', 'ARS', 'GOAL')
        alerts.observe('soccer', 'EPL', '1', [])
        alerts.observe('soccer', 'EPL', '1', [event])
        board = MultiSportRenderer(Renderer(), Renderer(), clock=lambda: now[0],
                                   scoring_alerts=alerts)
        during = frame_payload(board.frame())
        self.assertTrue(any(pixel != (0, 0, 0) for pixel in during['pixels']))
        now[0] = 2
        after = frame_payload(board.frame())
        self.assertTrue(all(pixel == (0, 0, 0) for pixel in after['pixels']))


if __name__ == '__main__':
    unittest.main()
