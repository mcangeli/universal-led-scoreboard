"""Color save guard prevents malformed RGB values from reaching the server."""
import unittest
from universal_led import configurator


class ColorSaveValidationTests(unittest.TestCase):
    def test_color_channels_require_three_valid_integers(self):
        html=configurator.HTML
        self.assertIn('function invalidColorEntry(palette)',html)
        self.assertIn("['scoreboard','teams']",html)
        self.assertIn('!Array.isArray(channels)||channels.length!==3',html)
        self.assertIn('!Number.isInteger(value)||value<0||value>255',html)

    def test_save_guard_runs_before_network_request(self):
        html=configurator.HTML
        start=html.index("document.getElementById('save').onclick=async()=>{")
        end=html.index('let nhlColors=null',start)
        section=html[start:end]
        self.assertIn('const invalid=invalidColorEntry(state);',section)
        self.assertIn('if(invalid)',section)
        self.assertLess(section.index('if(invalid)'),section.index("fetch('/api/config'"))


if __name__=='__main__':
    unittest.main()
