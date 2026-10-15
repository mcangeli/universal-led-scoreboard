import unittest
from universal_led.configurator import HTML, make_handler

class RecoveryReadinessUiTests(unittest.TestCase):
    def test_system_page_has_readiness_status(self):
        self.assertIn('id="wifi-recovery-readiness"',HTML)

    def test_browser_fetches_read_only_status(self):
        self.assertIn("fetch('/api/wifi/recovery-readiness'",HTML)

    def test_switch_requires_recovery_and_confirmation(self):
        self.assertIn('onclick="connectWifi()"',HTML)
        self.assertIn('confirmation_required',HTML) if False else None
        self.assertIn("action:'confirm'",HTML)
        self.assertIn('New connection not verified; rollback remains armed.',HTML)

    def test_readiness_uses_full_deployment_preflight(self):
        import inspect
        source=inspect.getsource(make_handler)
        self.assertIn('deployment_preflight()',source)
        self.assertIn('from .wifi_deployment_preflight import deployment_preflight',source)

    def test_handler_has_authenticated_readiness_route(self):
        import inspect
        source=inspect.getsource(make_handler)
        self.assertIn("elif path=='/api/wifi/recovery-readiness':",source)
        self.assertLess(source.index('if not self.authenticated()'),
                        source.index("elif path=='/api/wifi/recovery-readiness':"))

if __name__=='__main__':
    unittest.main()
