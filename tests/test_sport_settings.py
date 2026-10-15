import copy
import tempfile
import unittest
from universal_led.sport_settings import DEFAULT_SETTINGS,validate_settings,load_settings,save_settings

class SportSettingsTests(unittest.TestCase):
    def test_defaults(self):
        self.assertEqual(validate_settings(copy.deepcopy(DEFAULT_SETTINGS))['active_sport'],'mlb')
    def test_persistence(self):
        with tempfile.TemporaryDirectory() as root:
            changed=copy.deepcopy(DEFAULT_SETTINGS)
            changed['mlb']['favorite_teams']=['NYM']
            save_settings(root,changed)
            self.assertEqual(load_settings(root)['mlb']['favorite_teams'],['NYM'])
    def test_reject_unsupported_active_sport(self):
        data=copy.deepcopy(DEFAULT_SETTINGS)
        data['sports']['nba']['enabled']=True
        data['active_sport']='nba'
        with self.assertRaises(ValueError):validate_settings(data)
    def test_reject_bad_refresh(self):
        data=copy.deepcopy(DEFAULT_SETTINGS)
        data['mlb']['refresh_seconds']=0
        with self.assertRaises(ValueError):validate_settings(data)
    def test_reject_unknown_keys(self):
        data=copy.deepcopy(DEFAULT_SETTINGS)
        data['malicious']='value'
        with self.assertRaises(ValueError):validate_settings(data)
if __name__=='__main__':
    unittest.main()
