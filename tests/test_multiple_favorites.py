import copy
import unittest
from universal_led.mlb_classic import BaseballGame
from universal_led.mlb_runtime import select_games
from universal_led.sport_settings import DEFAULT_SETTINGS,validate_settings


class MultipleFavoriteTests(unittest.TestCase):
    def test_legacy_single_favorite_migrates(self):
        settings=copy.deepcopy(DEFAULT_SETTINGS)
        settings['mlb']['favorite_team']=settings['mlb'].pop('favorite_teams')[0]
        result=validate_settings(settings)
        self.assertEqual(result['mlb']['favorite_teams'],['ATL'])
        self.assertNotIn('favorite_team',result['mlb'])

    def test_multiple_favorites_and_duplicate_rejection(self):
        settings=copy.deepcopy(DEFAULT_SETTINGS)
        settings['mlb']['favorite_teams']=['ATL','NYM']
        self.assertEqual(validate_settings(settings)['mlb']['favorite_teams'],['ATL','NYM'])
        settings['mlb']['favorite_teams']=['ATL','ATL']
        with self.assertRaises(ValueError):
            validate_settings(settings)

    def test_favorite_filter_and_fallback(self):
        games=[BaseballGame(away='ATL',home='NYM'),BaseballGame(away='BOS',home='NYY'),
               BaseballGame(away='LAD',home='SFG')]
        self.assertEqual(select_games(games,['ATL','NYM'],'favorite'),[games[0]])
        self.assertEqual(select_games(games,['BOS','SFG'],'favorite'),[games[1],games[2]])
        self.assertEqual(select_games(games,['MIA'],'fallback'),games)
        self.assertEqual(select_games(games,['MIA'],'favorite'),[])

    def test_single_team_callers_remain_supported(self):
        games=[BaseballGame(away='ATL',home='NYM')]
        self.assertEqual(select_games(games,'ATL','favorite'),games)


if __name__=='__main__':
    unittest.main()
