"""RSS source editor performs client-side validation before POST."""
import unittest
from universal_led import configurator


class NewsSourceValidationUITests(unittest.TestCase):
    def test_missing_name_and_category_are_rejected(self):
        html=configurator.HTML
        self.assertIn("label+' needs a name.'",html)
        self.assertIn("label+' needs a category.'",html)

    def test_http_or_https_url_required(self):
        html=configurator.HTML
        self.assertIn('source.url.trim()',html)
        self.assertIn('valid HTTP or HTTPS URL',html)

    def test_refresh_interval_is_bounded_integer(self):
        html=configurator.HTML
        self.assertIn('!Number.isInteger(source.refresh_seconds)',html)
        self.assertIn('source.refresh_seconds<60||source.refresh_seconds>86400',html)


if __name__=='__main__':
    unittest.main()
