"""Regression coverage for native plugin uninstall UI and registry behavior."""
import json
import tempfile
import unittest
from pathlib import Path

from universal_led.configurator import HTML
from universal_led.plugin_registry import uninstall_plugin
from universal_led.plugin_manifest import ManifestError


class PluginUninstallDashboardTests(unittest.TestCase):
    def test_dashboard_has_uninstall_action(self):
        self.assertIn('async function removePlugin(id)', HTML)
        self.assertIn('/api/plugins/uninstall', HTML)
        self.assertIn('if(!plugin.enabled)', HTML)

    def test_uninstall_requires_disabled_plugin_and_preserves_external_data(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp) / 'plugins'
            root.mkdir()
            package = root / 'sample'
            package.mkdir()
            (package / 'plugin.py').write_text('pass\\n')
            registry = Path(temp) / 'plugins.json'
            data = Path(temp) / 'plugin-settings'
            data.mkdir()
            (data / 'sample.json').write_text('{"display_seconds":12}')
            entry = {'id':'sample','version':'0.1.0',
                     'source':'https://github.com/example/sample',
                     'commit':'a'*40,'enabled':True}
            registry.write_text(json.dumps({'sample':entry}))
            with self.assertRaises(ManifestError):
                uninstall_plugin(root,registry,'sample')
            self.assertTrue(package.exists())
            entry['enabled'] = False
            registry.write_text(json.dumps({'sample':entry}))
            result = uninstall_plugin(root,registry,'sample')
            self.assertEqual(result['id'],'sample')
            self.assertFalse(package.exists())
            self.assertEqual(json.loads(registry.read_text()),{})
            self.assertTrue((data / 'sample.json').exists())


if __name__ == '__main__':
    unittest.main()
