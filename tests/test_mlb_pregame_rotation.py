import unittest
from universal_led.mlb_classic import BaseballGame
from universal_led.mlb_data import parse_schedule
from universal_led.mlb_palette_v11 import MLBPaletteScreen

class PregameRotationTests(unittest.TestCase):
    def test_schedule_probables_and_records(self):
        side=lambda id, name: {'team':{'id':id},'leagueRecord':{'wins':20,'losses':10},
                                'probablePitcher':{'fullName':name}}
        payload={'dates':[{'games':[{'status':{'abstractGameState':'Preview'},
                   'teams':{'away':side(144,'Chris Sale'),'home':side(121,'Sean Manaea')}}]}]}
        game=parse_schedule(payload)[0]
        self.assertEqual(game.away_probable,'Chris Sale')
        self.assertEqual(game.home_record,'20-10')
    def test_all_three_pregame_pages_render(self):
        game=BaseballGame(status='pregame',away='ATL',home='NYM',
                          away_probable='Chris Sale',home_probable='Sean Manaea',
                          away_record='20-10',home_record='19-11')
        frames=[MLBPaletteScreen(game,pregame_page=i).render() for i in range(3)]
        self.assertTrue(all((f.width,f.height)==(64,32) for f in frames))
        self.assertNotEqual(frames[0].pixels,frames[1].pixels)
        self.assertNotEqual(frames[1].pixels,frames[2].pixels)
    def test_missing_pitcher_and_record_do_not_crash(self):
        game=BaseballGame(status='pregame')
        for i in range(3):
            self.assertEqual(MLBPaletteScreen(game,pregame_page=i).render().width,64)

if __name__=='__main__':
    unittest.main()
