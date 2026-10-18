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
    def test_allow_nba_active_sport(self):
        data=copy.deepcopy(DEFAULT_SETTINGS)
        data['sports']['nba']['enabled']=True
        data['active_sport']='nba'
        self.assertEqual(validate_settings(data)['active_sport'], 'nba')
    def test_allow_nfl_active_sport(self):
        data=copy.deepcopy(DEFAULT_SETTINGS)
        data['sports']['nfl']['enabled']=True
        data['active_sport']='nfl'
        self.assertEqual(validate_settings(data)['active_sport'], 'nfl')
    def test_reject_unsupported_active_sport(self):
        for sport in ('efl',):
            with self.subTest(sport=sport):
                data=copy.deepcopy(DEFAULT_SETTINGS)
                data['sports'][sport]['enabled']=True
                data['active_sport']=sport
                with self.assertRaises(ValueError):
                    validate_settings(data)
    def test_legacy_settings_without_nba(self):
        data=copy.deepcopy(DEFAULT_SETTINGS)
        del data['nba']
        self.assertEqual(validate_settings(data)['nba'], DEFAULT_SETTINGS['nba'])
    def test_reject_bad_refresh(self):
        data=copy.deepcopy(DEFAULT_SETTINGS)
        data['mlb']['refresh_seconds']=0
        with self.assertRaises(ValueError):validate_settings(data)
    def test_scoring_alert_defaults_are_disabled(self):
        self.assertEqual(validate_settings(copy.deepcopy(DEFAULT_SETTINGS))['scoring_alerts'],
                         {'enabled':False,'scope':'favorites','seconds':8})

    def test_legacy_settings_without_scoring_alerts(self):
        data=copy.deepcopy(DEFAULT_SETTINGS)
        del data['scoring_alerts']
        self.assertEqual(validate_settings(data)['scoring_alerts'],
                         DEFAULT_SETTINGS['scoring_alerts'])

    def test_scoring_alert_settings_roundtrip(self):
        with tempfile.TemporaryDirectory() as root:
            data=copy.deepcopy(DEFAULT_SETTINGS)
            data['scoring_alerts']={'enabled':True,'scope':'all','seconds':12}
            save_settings(root,data)
            self.assertEqual(load_settings(root)['scoring_alerts'],data['scoring_alerts'])

    def test_scoring_alert_invalid_options_rejected(self):
        for option,bad in (('enabled',1),('scope','anything'),('seconds',0),('seconds',61)):
            with self.subTest(option=option,bad=bad):
                data=copy.deepcopy(DEFAULT_SETTINGS)
                data['scoring_alerts'][option]=bad
                with self.assertRaises(ValueError):
                    validate_settings(data)

    def test_reject_unknown_keys(self):
        data=copy.deepcopy(DEFAULT_SETTINGS)
        data['malicious']='value'
        with self.assertRaises(ValueError):validate_settings(data)
if __name__=='__main__':
    unittest.main()
