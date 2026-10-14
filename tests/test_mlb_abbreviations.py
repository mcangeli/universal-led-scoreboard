import unittest
from universal_led.mlb_data import parse_schedule,team_abbreviation,TEAM_ABBREVIATIONS
from universal_led.mlb_visual import TEAM_COLORS

class MLBAbbreviationTests(unittest.TestCase):
    def test_all_known_teams_match_palette(self):
        self.assertEqual(len(TEAM_ABBREVIATIONS),30)
        self.assertTrue(set(TEAM_ABBREVIATIONS.values()).issubset(TEAM_COLORS))
    def test_dodgers_from_id(self):
        self.assertEqual(team_abbreviation({'id':119,'name':'Los Angeles Dodgers'}),'LAD')
    def test_brewers_from_id(self):
        self.assertEqual(team_abbreviation({'id':158,'name':'Milwaukee Brewers'}),'MIL')
    def test_name_fallback(self):
        self.assertEqual(team_abbreviation({'name':'Los Angeles Dodgers'}),'LAD')
    def test_schedule_without_abbreviation(self):
        payload={'dates':[{'games':[{'teams':{
            'away':{'team':{'id':158,'name':'Milwaukee Brewers'}},
            'home':{'team':{'id':119,'name':'Los Angeles Dodgers'}}},
            'status':{'abstractGameState':'Preview'}}]}]}
        game=parse_schedule(payload)[0]
        self.assertEqual((game.away,game.home),('MIL','LAD'))
    def test_id_overrides_bad_abbreviation(self):
        self.assertEqual(team_abbreviation({'id':119,'abbreviation':'LOS'}),'LAD')

if __name__=='__main__':
    unittest.main()
