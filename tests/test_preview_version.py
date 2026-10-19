import unittest
from unittest.mock import patch

from universal_led import __version__
from universal_led.release import display_version
from universal_led.configurator import HTML


class PreviewVersionTests(unittest.TestCase):
    def test_current_version_label(self):
        with patch('universal_led.release.installed_commit',return_value='abc12345'), \
             patch('universal_led.release.installed_release',return_value='feature/0.7.0-scoring-standings'):
            self.assertEqual(display_version(),f'v{__version__} · feature/0.7.0-scoring-standings · abc12345')

    def test_dashboard_uses_dynamic_label(self):
        self.assertIn('__PREVIEW_VERSION__',HTML)
        self.assertNotIn('Preview 21.3',HTML)

    def test_version_marker_replaces_cleanly(self):
        with patch('universal_led.release.installed_commit',return_value='abc12345'), \
             patch('universal_led.release.installed_release',return_value='feature/0.7.0-scoring-standings'):
            rendered=HTML.replace('__PREVIEW_VERSION__',display_version())
        self.assertIn(f'<span class="muted">v{__version__} · feature/0.7.0-scoring-standings · abc12345</span>',rendered)
        self.assertNotIn('__PREVIEW_VERSION__',rendered)


if __name__ == '__main__':
    unittest.main()
