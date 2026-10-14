import unittest
from universal_led.mlb_data import MLBFeed, parse_schedule

PAYLOAD={'dates':[{'games':[{
 'teams':{'away':{'team':{'abbreviation':'NYM'},'score':2},
          'home':{'team':{'abbreviation':'ATL'},'score':4}},
 'status':{'abstractGameState':'Live'},
 'linescore':{'currentInning':7,'isTopInning':False,'outs':1,
              'offense':{'first':{'id':1},'third':{'id':3}},
              'teams':{'away':{'hits':5,'errors':0},'home':{'hits':8,'errors':1}}}
}]}]}

class MLBDataTests(unittest.TestCase):
    def test_live_game(self):
        g=parse_schedule(PAYLOAD)[0]
        self.assertEqual((g.away,g.home,g.home_runs),('NYM','ATL',4))
        self.assertEqual(g.bases,(True,False,True))
        self.assertEqual(g.inning_half,'bottom')
        self.assertEqual(g.home_hits,8)
    def test_filter(self):
        self.assertEqual(len(parse_schedule(PAYLOAD,'ATL')),1)
        self.assertEqual(parse_schedule(PAYLOAD,'LAD'),[])
    def test_empty(self):
        self.assertEqual(parse_schedule({'dates':[]}),[])
    def test_status(self):
        for value,expected in [('Final','final'),('Preview','pregame'),('Live','live')]:
            obj={'dates':[{'games':[dict(PAYLOAD['dates'][0]['games'][0],status={'abstractGameState':value})]}]}
            self.assertEqual(parse_schedule(obj)[0].status,expected)
    def test_cache_and_failure(self):
        now=[10.]
        calls=[0]
        def fetch():
            calls[0]+=1
            if calls[0]>1: raise OSError('offline')
            return PAYLOAD
        feed=MLBFeed(fetch=fetch,clock=lambda:now[0],refresh_seconds=60)
        self.assertEqual(len(feed.games()),1)
        self.assertEqual(len(feed.games()),1)
        self.assertEqual(calls[0],1)
        now[0]=71.
        self.assertEqual(len(feed.games()),1)
        self.assertEqual(calls[0],2)
        self.assertEqual(feed.last_error,'offline')
    def test_invalid_refresh(self):
        with self.assertRaises(ValueError):
            MLBFeed(refresh_seconds=0)

if __name__=='__main__':
    unittest.main()
