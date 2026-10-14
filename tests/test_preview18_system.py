import unittest
from unittest.mock import patch
from universal_led.system_diagnostics import system_status, service_status
from universal_led.configurator import HTML

class SystemDiagnosticsTests(unittest.TestCase):
    def test_status_has_expected_fields(self):
        status=system_status()
        for key in ('model','hostname','temperature_c','disk_free_gb','service','led_hardware'):
            self.assertIn(key,status)
        self.assertEqual(status['led_hardware'],'not configured')
    def test_service_unavailable(self):
        with patch('universal_led.system_diagnostics.subprocess.run',side_effect=OSError('missing')):
            self.assertEqual(service_status()['state'],'unavailable')
    def test_system_ui(self):
        self.assertIn('/api/system',HTML)
        self.assertIn('pi-info',HTML)
        self.assertIn('refreshSystem()',HTML)

if __name__=='__main__':
    unittest.main()
