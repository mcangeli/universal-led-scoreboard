import unittest
from universal_led.mlb_classic import BaseballGame,GOLD,DIM,RED
from universal_led.mlb_classic_v9 import MLBClassicV9Screen,start_label
from universal_led.mlb_visual import TEAM_COLORS
from universal_led.mlb_data import parse_schedule

class ClassicV9Tests(unittest.TestCase):
    def test_native_dimensions(self):
        for status in ('live','pregame','final','delayed','postponed'):
            with self.subTest(status=status):
                f=MLBClassicV9Screen(BaseballGame(status=status)).render()
                self.assertEqual((f.width,f.height),(64,32))
                self.assertEqual(len(f.pixels),32)
                self.assertTrue(all(len(row)==64 for row in f.pixels))
    def test_team_colors(self):
        f=MLBClassicV9Screen().render()
        self.assertIn(TEAM_COLORS['NYM'],f.pixels[7])
        self.assertIn(TEAM_COLORS['ATL'],f.pixels[17])
    def test_live_bases_outs(self):
        f=MLBClassicV9Screen().render()
        self.assertEqual(f.pixels[29][45],GOLD)
        self.assertEqual(f.pixels[27][50],DIM)
        self.assertEqual(f.pixels[28][20],RED)
    def test_large_score_indicator(self):
        f=MLBClassicV9Screen(BaseballGame(away_runs=100)).render()
        self.assertEqual(f.pixels[9][34],RED)
    def test_start_time_fallback(self):
        self.assertEqual(start_label(None),'PREGAME')
        self.assertEqual(start_label('bad-date'),'PREGAME')
    def test_api_game_date(self):
        date='2026-10-14T23:05:00Z'
        payload={'dates':[{'games':[{'gameDate':date,
            'teams':{'away':{'team':{'abbreviation':'NYM'}},
                     'home':{'team':{'abbreviation':'ATL'}}},
            'status':{'abstractGameState':'Preview'}}]}]}
        self.assertEqual(parse_schedule(payload)[0].start_time,date)
if __name__=='__main__':
    unittest.main()
