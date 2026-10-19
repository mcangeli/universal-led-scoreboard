"""Ensure browser and matrix render through the same scoring-alert scheduler."""
import inspect
import unittest

from universal_led import configurator
from universal_led.multisport_runtime import MultiSportRenderer
from universal_led.scoring_alerts import ScoreEvent, ScoringAlerts


class Renderer:
    def frame(self):
        return "normal-frame"


class ScoringAlertLiveSettingsTests(unittest.TestCase):
    def test_settings_endpoint_applies_changes_to_running_process(self):
        source = inspect.getsource(configurator.make_handler)
        self.assertIn("if settings_callback:settings_callback(saved_settings)", source)
        startup = inspect.getsource(configurator.main)
        self.assertIn("scoring_alerts.configure(**settings['scoring_alerts'])", startup)

    def test_browser_preview_and_frame_publisher_share_board(self):
        startup = inspect.getsource(configurator.main)
        self.assertIn("write_frame(frame_path, board.frame())", startup)
        self.assertIn("feed_status,board.frame,countdown_status", startup)

    def test_alert_toggle_during_match_restores_board_and_no_replay(self):
        now = [0]
        alerts = ScoringAlerts(enabled=False)
        board = MultiSportRenderer(Renderer(), Renderer(), clock=lambda: now[0],
                                   scoring_alerts=alerts,
                                   alert_renderer=lambda event: "GOAL:" + event.event_id)
        goal = ScoreEvent("soccer", "EPL", "fixture", "goal-1", "ARS", "GOAL")
        alerts.observe("soccer", "EPL", "fixture", [])
        alerts.observe("soccer", "EPL", "fixture", [goal])
        alerts.configure(enabled=True, scope="all", seconds=4)
        self.assertEqual(board.frame(), "normal-frame")
        newer = ScoreEvent("soccer", "EPL", "fixture", "goal-2", "ARS", "GOAL")
        alerts.observe("soccer", "EPL", "fixture", [goal, newer])
        self.assertEqual(board.frame(), "GOAL:goal-2")
        alerts.configure(enabled=False)
        self.assertEqual(board.frame(), "normal-frame")
        alerts.configure(enabled=True, scope="all", seconds=4)
        self.assertEqual(board.frame(), "normal-frame")

    def test_preview_and_matrix_calls_show_same_active_alert(self):
        now = [0]
        alerts = ScoringAlerts(enabled=True, scope="all", seconds=3)
        board = MultiSportRenderer(Renderer(), Renderer(), clock=lambda: now[0],
                                   scoring_alerts=alerts,
                                   alert_renderer=lambda event: "GOAL:" + event.event_id)
        goal = ScoreEvent("soccer", "EPL", "fixture", "goal-1", "ARS", "GOAL")
        alerts.observe("soccer", "EPL", "fixture", [])
        alerts.observe("soccer", "EPL", "fixture", [goal])
        self.assertEqual(board.frame(), "GOAL:goal-1")
        now[0] = 1
        self.assertEqual(board.frame(), "GOAL:goal-1")
        now[0] = 3
        self.assertEqual(board.frame(), "normal-frame")


if __name__ == "__main__":
    unittest.main()
