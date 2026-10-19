"""Exercise NHL refresh, goal queue and display metadata together."""
import unittest
from datetime import date
from universal_led.nhl_feed import NHLFeed
from universal_led.nhl_runtime import BackgroundNHLFeed
from universal_led.nhl_engine import ConfiguredNHLRenderer
from universal_led.scoring_alerts import ScoringAlerts
from universal_led.scoring_alert_screen import render_scoring_alert


class NHLGoalPipelineTests(unittest.TestCase):
    def make_pipeline(self):
        scores=[0,0]
        def fetch(_day):
            return {'games':[{'id':123,'gameState':'LIVE','awayTeam':{'abbrev':'BOS','score':scores[0]},'homeTeam':{'abbrev':'NYR','score':scores[1]}}]}
        ticks=[0]
        feed=NHLFeed(fetcher=fetch,refresh_seconds=5,clock=lambda:ticks[0])
        worker=BackgroundNHLFeed(feed,day_provider=lambda:date(2026,10,19))
        alerts=ScoringAlerts(enabled=True,scope='all')
        renderer=ConfiguredNHLRenderer(worker,scoring_alerts=alerts)
        worker.on_games=lambda games:renderer.score_observer.observe(games,favorite_teams=renderer.favorite_teams)
        return scores,ticks,worker,alerts

    def test_live_refresh_enqueues_goal_with_matchup_score(self):
        scores,ticks,worker,alerts=self.make_pipeline()
        worker.refresh_once()
        scores[0]=1
        ticks[0]=6
        worker.refresh_once()
        event=alerts.next_alert(10)
        self.assertIsNotNone(event)
        self.assertEqual((event.sport,event.kind,event.team_id),('nhl','GOAL','BOS'))
        self.assertEqual((event.away_team,event.away_score,event.home_team,event.home_score),('BOS',1,'NYR',0))
        self.assertIsNotNone(render_scoring_alert(event))

    def test_repeated_refresh_does_not_enqueue_duplicate(self):
        scores,ticks,worker,alerts=self.make_pipeline()
        worker.refresh_once()
        scores[1]=1
        ticks[0]=6
        worker.refresh_once()
        self.assertIsNotNone(alerts.next_alert(10))
        ticks[0]=12
        worker.refresh_once()
        self.assertIsNone(alerts.next_alert(19))

    def test_failed_refresh_does_not_generate_goal(self):
        scores,ticks,worker,alerts=self.make_pipeline()
        worker.refresh_once()
        worker.feed.fetcher=lambda day: (_ for _ in ()).throw(OSError('offline'))
        ticks[0]=6
        worker.refresh_once()
        self.assertIsNone(alerts.next_alert(10))


if __name__=='__main__':
    unittest.main()
