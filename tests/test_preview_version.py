import unittest
from universal_led.release import display_version
from universal_led.configurator import HTML

class PreviewVersionTests(unittest.TestCase):
    def test_current_preview_label(self):
        self.assertEqual(display_version(), 'Preview 21.6 · Stage 12')

    def test_dashboard_uses_dynamic_label(self):
        self.assertIn('__PREVIEW_VERSION__', HTML)
        self.assertNotIn('Preview 21.3', HTML)

    def test_version_marker_replaces_cleanly(self):
        rendered=HTML.replace('__PREVIEW_VERSION__',display_version())
        self.assertIn('Native Configurator | Preview 21.6 · Stage 12',rendered)
        self.assertNotIn('__PREVIEW_VERSION__',rendered)

if __name__ == '__main__':
    unittest.main()
