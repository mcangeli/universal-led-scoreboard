import tempfile
import unittest
from universal_led.news_settings import load_news_settings, save_news_settings, validate_news_settings
from universal_led.configurator import HTML


class NewsSettingsTests(unittest.TestCase):
    def test_empty_defaults(self):
        with tempfile.TemporaryDirectory() as directory:
            self.assertEqual(load_news_settings(directory), {'sources': []})

    def test_round_trip(self):
        with tempfile.TemporaryDirectory() as directory:
            data={'sources':[{'name':'Baseball','url':'https://example.com/rss','category':'mlb','enabled':True,'refresh_seconds':900}]}
            self.assertEqual(save_news_settings(directory,data),data)
            self.assertEqual(load_news_settings(directory),data)

    def test_rejects_invalid_url_and_duplicate_names(self):
        source={'name':'News','url':'https://example.com/feed'}
        with self.assertRaises(ValueError):
            validate_news_settings({'sources':[dict(source,url='file:///etc/passwd')]})
        with self.assertRaises(ValueError):
            validate_news_settings({'sources':[source,dict(source,name='news')]})

    def test_rejects_excessive_sources(self):
        with self.assertRaises(ValueError):
            validate_news_settings({'sources':[{'name':str(i),'url':'https://example.com'} for i in range(21)]})

    def test_configurator_exposes_editor(self):
        self.assertIn('data-page="news"',HTML)
        self.assertIn('saveNewsSources()',HTML)
        self.assertIn('Automatic and custom feeds display during available news rotation slots.',HTML)


if __name__=='__main__':
    unittest.main()
