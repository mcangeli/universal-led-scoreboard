"""End-to-end software-frame checks for Championship favorite goal interruptions.

No network, wall clock, or physical LED matrix is required.
"""
import unittest

from universal_led.display import Framebuffer
from universal_led.multisport_runtime import MultiSportRenderer
from universal_led.scoring_alerts import ScoringAlerts, ScoreEvent
from universal_led.scoring_alert_eligibility import scoring_event_eligible
from universal_led.scoring_alert_screen import render_scoring_alert


class GameRenderer:
    def __init__(self):
        self.calls = 0

    def frame(self):
        self.calls += 1
        frame = Framebuffer()
        frame.pixel(0, 0, (15, 70, 130))
        return frame


class ChampionshipAlertFrameTests(unittest.TestCase):
    def setUp(self):
        self.now = [100.]
        self.game = GameRenderer()
        self.settings = {
            "sports": {"english": {"enabled": True}},
            "english": {"mode": "favorite", "favorite_teams": ["espn:555"]},
        }
        self.alerts = ScoringAlerts(enabled=True, scope="favorites", seconds=4)
        self.alerts.set_eligibility(lambda event: scoring_event_eligible(event, self.settings))
        self.board = MultiSportRenderer(self.game, self.game,
                                        clock=lambda: self.now[0],
                                        scoring_alerts=self.alerts)
        self.board.set_active_sport("mlb")

    def goal(self, scorer="OTH", game="wrexham", home_key="espn:555"):
        return ScoreEvent(
            sport="soccer", league="CHAMPIONSHIP", game_id=game,
            event_id="goal-1", team_id=scorer, kind="GOAL",
            home_team="WRE", away_team="OTH", home_score=1, away_score=1,
            home_club_key=home_key, away_club_key="espn:777",
        )

    def observe(self, event):
        self.alerts.baseline(event.sport, event.league, event.game_id, ())
        return self.alerts.observe(event.sport, event.league, event.game_id,
                                   (event,), favorite_teams=("espn:555",))

    def test_opponent_goal_renders_real_64x32_card_then_resumes(self):
        normal = self.board.frame()
        self.assertEqual(normal.pixels[0][0], (15, 70, 130))
        event = self.goal()
        self.assertEqual(self.observe(event), (event,))
        alert = self.board.frame()
        self.assertIsInstance(alert, Framebuffer)
        self.assertEqual((alert.width, alert.height), (64, 32))
        self.assertEqual(alert.pixels[9][0], (85, 100, 115))
        self.assertNotEqual(alert.ppm(), normal.ppm())
        self.assertEqual(self.board.frame().ppm(), alert.ppm())
        self.now[0] += 4
        self.assertEqual(self.board.frame().ppm(), normal.ppm())

    def test_favorite_goal_renders_without_duplicate_replay(self):
        event = self.goal(scorer="WRE")
        self.observe(event)
        self.assertEqual(self.board.frame().pixels[9][0], (85, 100, 115))
        self.now[0] += 4
        self.assertEqual(self.board.frame().pixels[0][0], (15, 70, 130))
        self.assertEqual(self.alerts.observe(event.sport, event.league, event.game_id,
                                             (event,), favorite_teams=("espn:555",)), ())
        self.assertEqual(self.board.frame().pixels[0][0], (15, 70, 130))

    def test_unrelated_championship_match_does_not_interrupt(self):
        event = self.goal(game="other", home_key="espn:111")
        self.assertEqual(self.observe(event), ())
        self.assertEqual(self.board.frame().pixels[0][0], (15, 70, 130))

    def test_native_alert_renderer_produces_valid_ppm(self):
        image = render_scoring_alert(self.goal())
        ppm = image.ppm()
        self.assertTrue(ppm.startswith(b"P6\n64 32\n255\n"))
        self.assertEqual(len(ppm), len(b"P6\n64 32\n255\n") + 64 * 32 * 3)


if __name__ == "__main__":
    unittest.main()
