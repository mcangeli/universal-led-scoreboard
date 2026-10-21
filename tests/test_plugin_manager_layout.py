"""Plugin Manager sections reflect distinct plugin sources and lifecycle states."""
import unittest
from universal_led.configurator import HTML
from universal_led.official_plugin_catalog import read_official_catalog


class PluginManagerLayoutTests(unittest.TestCase):
    def test_distinct_sections(self):
        for heading in ('Installed plugins', 'Available plugins', 'Bundled examples', 'Install from GitHub'):
            self.assertIn(heading, HTML)
        self.assertIn('id="plugin-available"', HTML)
        self.assertIn('Refresh catalog', HTML)
        self.assertLess(HTML.index('<h3>Install from GitHub</h3>'), HTML.index('<h3>Available plugins</h3>'))
        self.assertIn('id="plugin-bundled-state"', HTML)
        self.assertIn('bundledInstall.hidden=helloInstalled', HTML)
        self.assertNotIn('Plugin management preview only.', HTML)
        self.assertNotIn('Enabling does not yet add a plugin to live rotation.', HTML)

    def test_official_catalog_includes_toml_plugins(self):
        catalog = {item['id']:item for item in read_official_catalog()}
        self.assertEqual(catalog['swimming-fish']['version'], '0.2.0')
        self.assertEqual(catalog['disney-wait-times']['version'], '0.2.0')
        self.assertEqual(catalog['daily-calendar']['version'], '0.1.0')
        self.assertNotIn('hello-world', catalog)


if __name__ == '__main__':
    unittest.main()
