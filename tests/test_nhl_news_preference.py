import unittest
from universal_led.configurator import HTML
from universal_led.sport_settings import DEFAULT_SETTINGS, validate_settings


class NHLNewsPreferenceTests(unittest.TestCase):
    def test_independent_nhl_news_control(self):
        self.assertIn('id="nhl-news-enabled"', HTML)
        self.assertIn("data.sports.nhl.news_enabled=document.getElementById('nhl-news-enabled').checked", HTML)
        self.assertIn("document.getElementById('nhl-news-enabled').checked=data.sports.nhl.news_enabled", HTML)

    def test_news_preferences_are_independent(self):
        import copy
        data=copy.deepcopy(DEFAULT_SETTINGS)
        data['sports']['nhl']['enabled']=True
        data['sports']['nhl']['news_enabled']=True
        data['sports']['mlb']['news_enabled']=False
        result=validate_settings(data)
        self.assertTrue(result['sports']['nhl']['news_enabled'])
        self.assertFalse(result['sports']['mlb']['news_enabled'])


if __name__=='__main__':
    unittest.main()
