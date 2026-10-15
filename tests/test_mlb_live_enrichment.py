import unittest
from universal_led.mlb_classic import BaseballGame
from universal_led.mlb_runtime import BackgroundMLBFeed


class FakeFeed:
    refresh_seconds=60
    last_error=None
    def __init__(self,games):
        self._games=games
    def games(self):
        return self._games


class LiveEnrichmentTests(unittest.TestCase):
    def test_enriches_only_live_games(self):
        calls=[]
        def fetch(pk):
            calls.append(pk)
            return {'liveData':{'plays':{'currentPlay':{'matchup':{'pitcher':{'id':7}},
                'playEvents':[{'pitchData':{'startSpeed':97.1}}]},
                'allPlays':[]},'boxscore':{'teams':{'away':{'players':{
                'ID7':{'stats':{'pitching':{'numberOfPitches':52}}}}}}}}}
        worker=BackgroundMLBFeed(FakeFeed([
            BaseballGame(game_pk=100,status='live'),
            BaseballGame(game_pk=101,status='final')]),fetch_live=fetch)
        worker.refresh_once()
        games=worker.games()
        self.assertEqual(calls,[100])
        self.assertEqual(games[0].pitch_count,52)
        self.assertEqual(games[0].pitch_speed_mph,97.1)
        self.assertIsNone(games[1].pitch_count)
        self.assertIsNone(worker.live_error)

    def test_live_feed_failure_keeps_schedule_score(self):
        def fail(pk):
            raise OSError('offline')
        worker=BackgroundMLBFeed(FakeFeed([
            BaseballGame(game_pk=100,status='live',home_runs=8)]),fetch_live=fail)
        worker.refresh_once()
        self.assertEqual(worker.games()[0].home_runs,8)
        self.assertIsNone(worker.last_error)
        self.assertIn('offline',worker.live_error)

    def test_missing_game_id_skips_supplemental_fetch(self):
        worker=BackgroundMLBFeed(FakeFeed([
            BaseballGame(game_pk=None,status='live')]),
            fetch_live=lambda pk: self.fail('unexpected fetch'))
        worker.refresh_once()
        self.assertEqual(len(worker.games()),1)


if __name__=='__main__':
    unittest.main()
