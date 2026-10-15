import copy
import tempfile
import unittest
from universal_led.sport_settings import DEFAULT_SETTINGS, validate_settings, load_settings, save_settings
from universal_led.automatic_news import AutomaticSportsNews
from universal_led.configurator import HTML


class StubNews:
    def items(self):
        return ['headline']


class AutomaticNewsTests(unittest.TestCase):
    def test_mlb_enabled_by_default(self):
        self.assertTrue(load_settings('/path/that/does/not/exist')['sports']['mlb']['news_enabled'])

    def test_legacy_settings_upgrade(self):
        legacy=copy.deepcopy(DEFAULT_SETTINGS)
        for sport in legacy['sports'].values():
            del sport['news_enabled']
        result=validate_settings(legacy)
        self.assertTrue(result['sports']['mlb']['news_enabled'])
        self.assertFalse(result['sports']['nba']['news_enabled'])

    def test_toggle_persists(self):
        with tempfile.TemporaryDirectory() as directory:
            settings=copy.deepcopy(DEFAULT_SETTINGS)
            settings['sports']['mlb']['news_enabled']=False
            save_settings(directory,settings)
            self.assertFalse(load_settings(directory)['sports']['mlb']['news_enabled'])

    def test_provider_respects_toggle(self):
        settings=copy.deepcopy(DEFAULT_SETTINGS)
        registry=AutomaticSportsNews({'mlb':StubNews()})
        self.assertEqual(registry.items(settings),['headline'])
        settings['sports']['mlb']['news_enabled']=False
        self.assertEqual(registry.items(settings),[])

    def test_news_toggle_is_present(self):
        self.assertIn('id="mlb-news-enabled"',HTML)
        self.assertIn('saveAutomaticNews()',HTML)


if __name__=='__main__':
    unittest.main()
