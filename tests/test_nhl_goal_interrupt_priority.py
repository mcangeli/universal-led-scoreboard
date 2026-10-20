"""NHL goal events interrupt other sport screens and restore rotation afterward."""
import unittest
from types import SimpleNamespace
from universal_led.multisport_runtime import MultiSportRenderer
from universal_led.score_change_observer import NHLGoalObserver
from universal_led.scoring_alerts import ScoringAlerts


class FrameAdapter:
    def __init__(self, name): self.name=name
    def frame(self): return self.name
    def game(self): return SimpleNamespace(status='live')


class NHLGoalInterruptionTests(unittest.TestCase):
    def test_goal_interrupts_other_sport_and_resumes_after_duration(self):
        now=[0]
        alerts=ScoringAlerts(enabled=True,scope='all',seconds=5)
        mlb=FrameAdapter('MLB LIVE')
        nhl=FrameAdapter('NHL LIVE')
        board=MultiSportRenderer(mlb,nhl,clock=lambda:now[0],scoring_alerts=alerts,alert_renderer=lambda event:'GOAL '+event.team_id)
        board.set_active_sport('mlb')
        self.assertEqual(board.frame(),'MLB LIVE')
        observer=NHLGoalObserver(alerts)
        def game(score):
            return SimpleNamespace(game_id=42,away='BOS',home='NYR',away_score=score,home_score=0,status='live')
        observer.observe([game(0)])
        observer.observe([game(1)])
        self.assertEqual(board.frame(),'GOAL BOS')
        now[0]=4
        self.assertEqual(board.frame(),'GOAL BOS')
        now[0]=5
        self.assertEqual(board.frame(),'MLB LIVE')

    def test_disabled_alerts_do_not_interrupt(self):
        alerts=ScoringAlerts(enabled=False,scope='all')
        board=MultiSportRenderer(FrameAdapter('MLB LIVE'),FrameAdapter('NHL LIVE'),clock=lambda:0,scoring_alerts=alerts,alert_renderer=lambda event:'GOAL')
        self.assertEqual(board.frame(),'MLB LIVE')

    def test_alert_has_priority_over_final_handoff(self):
        alerts=ScoringAlerts(enabled=True,scope='all')
        board=MultiSportRenderer(FrameAdapter('MLB LIVE'),FrameAdapter('NHL LIVE'),clock=lambda:0,scoring_alerts=alerts,alert_renderer=lambda event:'GOAL')
        observer=NHLGoalObserver(alerts)
        def game(score):return SimpleNamespace(game_id=42,away='BOS',home='NYR',away_score=score,home_score=0,status='live')
        observer.observe([game(0)])
        observer.observe([game(1)])
        class Handoff:
            def next(self):raise AssertionError('handoff should not run during goal alert')
        board.final_handoff=Handoff()
        self.assertEqual(board.frame(),'GOAL')


if __name__=='__main__':
    unittest.main()
