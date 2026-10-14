import unittest
from universal_led.mlb_classic import BaseballGame
from universal_led.mlb_runtime import BackgroundMLBFeed, select_games
from universal_led.mlb_data import MLBFeed

class RuntimeTests(unittest.TestCase):
    def setUp(self):
        self.games = [BaseballGame(away='NYM',home='ATL'),
                      BaseballGame(away='LAD',home='SDP')]
    def test_favorite(self):
        self.assertEqual(len(select_games(self.games,'ATL','favorite')),1)
        self.assertEqual(select_games(self.games,'BOS','favorite'),[])
    def test_fallback(self):
        self.assertEqual(select_games(self.games,'BOS','fallback'),self.games)
        self.assertEqual(len(select_games(self.games,'ATL','fallback')),1)
    def test_all(self):
        self.assertEqual(select_games(self.games,'ATL','all'),self.games)
    def test_bad_mode(self):
        with self.assertRaises(ValueError):
            select_games(self.games,mode='wrong')
    def test_snapshot_and_failure(self):
        payload={'dates':[{'games':[{'teams':{
          'away':{'team':{'abbreviation':'NYM'}},
          'home':{'team':{'abbreviation':'ATL'}}},
          'status':{'abstractGameState':'Final'}}]}]}
        feed=MLBFeed(team=None,fetch=lambda:payload,clock=lambda:100,refresh_seconds=60)
        worker=BackgroundMLBFeed(feed)
        self.assertEqual(worker.games(),[])
        worker.refresh_once()
        self.assertEqual(len(worker.games()),1)
        snapshot=worker.games()
        snapshot.clear()
        self.assertEqual(len(worker.games()),1)

if __name__=='__main__':
    unittest.main()
