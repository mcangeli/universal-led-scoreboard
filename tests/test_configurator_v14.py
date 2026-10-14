import copy
import tempfile
import unittest
from universal_led.configurator import HTML,make_handler
from universal_led.sport_settings import DEFAULT_SETTINGS,load_settings,save_settings
from universal_led.runtime_settings import ConfiguredMLBRenderer
from universal_led.mlb_classic import BaseballGame

class FakeFeed:
    def games(self):
        return [BaseballGame(away='NYM',home='ATL'),
                BaseballGame(away='BOS',home='NYY')]

class ConfiguratorV14Tests(unittest.TestCase):
    def test_navigation(self):
        for page in ('dashboard','sports','colors','system'):
            self.assertIn("showPage('"+page+"')",HTML)
    def test_settings_api_markers(self):
        self.assertIn('/api/settings',HTML)
        self.assertTrue(make_handler('/tmp','token'))
    def test_runtime_settings(self):
        with tempfile.TemporaryDirectory() as directory:
            renderer=ConfiguredMLBRenderer(directory,FakeFeed())
            self.assertEqual(renderer.game().home,'ATL')
            settings=copy.deepcopy(DEFAULT_SETTINGS)
            settings['mlb']['favorite_team']='BOS'
            renderer.apply(settings)
            self.assertEqual(renderer.game().away,'BOS')
            self.assertEqual((renderer.frame().width,renderer.frame().height),(64,32))
    def test_settings_save(self):
        with tempfile.TemporaryDirectory() as directory:
            changed=copy.deepcopy(DEFAULT_SETTINGS)
            changed['mlb']['rotation_seconds']=9
            save_settings(directory,changed)
            self.assertEqual(load_settings(directory)['mlb']['rotation_seconds'],9)
if __name__=='__main__':
    unittest.main()
