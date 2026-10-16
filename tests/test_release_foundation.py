"""Release-foundation checks for secure Wi-Fi provisioning and rendered dashboard."""
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]


class ReleaseFoundationTests(unittest.TestCase):
    def test_system_install_and_update_refresh_wifi_helpers(self):
        for script in ('install-system.sh', 'uls-update'):
            source = (ROOT / 'scripts' / script).read_text()
            for helper in ('install-wifi-scan-helper.sh',
                           'install-wifi-control-helper.sh',
                           'provision-hotspot.sh'):
                with self.subTest(script=script, helper=helper):
                    self.assertIn(helper, source)

    def test_scoped_sudoers_authorize_web_service_account(self):
        for script in ('install-wifi-scan-helper.sh',
                       'install-wifi-control-helper.sh'):
            source = (ROOT / 'scripts' / script).read_text()
            with self.subTest(script=script):
                self.assertIn('"uls"', source)
                self.assertIn('visudo -cf', source)

    def test_hotspot_is_not_automatically_activated(self):
        source = (ROOT / 'scripts' / 'provision-hotspot.sh').read_text()
        self.assertIn('secrets.token_urlsafe(24)', source)
        self.assertIn('os.O_EXCL', source)
        self.assertIn('chmod 0600 "$SECRET_FILE"', source)
        self.assertIn('connection.autoconnect no', source)
        self.assertNotIn('nmcli connection up', source)
        self.assertIn('nmcli connection edit', source)
        self.assertIn('if (( NEW_PROFILE == 0 )); then', source)
        self.assertIn('Existing recovery hotspot profile preserved.', source)

    def test_dashboard_update_install_is_allowed_by_post_route_guard(self):
        source = (ROOT / 'universal_led' / 'configurator.py').read_text()
        guard = source.split("if path not in (", 1)[1].split("):", 1)[0]
        self.assertIn("'/api/update/install'", guard)
        self.assertIn("if path=='/api/update/install':", source)

    def test_rendered_dashboard_has_valid_javascript_string_escape(self):
        from universal_led.configurator import HTML
        self.assertIn("+'\\n'+", HTML)
        self.assertNotIn("+'\n'+", HTML)


if __name__ == '__main__':
    unittest.main()
