"""News timing form rejects invalid values before posting settings."""
import unittest
from universal_led import configurator


class NewsTimingValidationUITests(unittest.TestCase):
    def test_timing_ranges_match_controls(self):
        html=configurator.HTML
        self.assertIn("['news-interval',1,20,'News interval']",html)
        self.assertIn("['news-duration',3,120,'Headline duration']",html)
        self.assertIn("['news-speed',1,15,'Scroll speed']",html)

    def test_empty_fractional_and_out_of_range_rejected(self):
        html=configurator.HTML
        self.assertIn("input.value.trim()===''",html)
        self.assertIn('!Number.isInteger(value)',html)
        self.assertIn('value<min||value>max',html)

    def test_validation_reports_error_and_stops_before_fetch(self):
        html=configurator.HTML
        start=html.index('async function saveNewsTiming()')
        end=html.index('let newsSources=',start)
        fn=html[start:end]
        self.assertLess(fn.index('for(const [id,min,max,label] of fields)'),fn.index("fetch('/api/settings'"))
        self.assertIn("input.focus();return;",fn)


if __name__=='__main__':
    unittest.main()
