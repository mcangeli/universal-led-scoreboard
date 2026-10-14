import unittest
from universal_led.configurator import HTML, make_handler

class RecoveryReadinessUiTests(unittest.TestCase):
    def test_system_page_has_readiness_status(self):
        self.assertIn('id="wifi-recovery-readiness"',HTML)

    def test_browser_fetches_read_only_status(self):
        self.assertIn("fetch('/api/wifi/recovery-readiness'",HTML)

    def test_switch_button_stays_disabled(self):
        self.assertIn('disabled title="Requires recovery helper"',HTML)
        self.assertIn('Connect (coming soon)',HTML)

    def test_readiness_requires_source_integrity(self):
        import inspect
        source=inspect.getsource(make_handler)
        self.assertIn('inspect_source_match(source=source)',source)
        self.assertIn("with_name('wifi_recovery.py')",source)

    def test_handler_has_authenticated_readiness_route(self):
        import inspect
        source=inspect.getsource(make_handler)
        self.assertIn("elif path=='/api/wifi/recovery-readiness':",source)
        self.assertLess(source.index('if not self.authenticated()'),
                        source.index("elif path=='/api/wifi/recovery-readiness':"))

if __name__=='__main__':
    unittest.main()
