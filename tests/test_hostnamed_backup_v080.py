"""Portable backup downloads include source hostname in their filename."""
import inspect
import unittest
from universal_led import configurator


class HostnamedBackupTests(unittest.TestCase):
    def test_server_uses_sanitized_device_hostname(self):
        source = inspect.getsource(configurator)
        self.assertIn("socket.gethostname()", source)
        self.assertIn("hostname=re.sub(", source)
        self.assertIn("portable-backup-'+time.strftime('%Y-%m-%d')+'.zip'", source)
        self.assertIn("self.send_header('Content-Disposition','attachment; filename\"'+filename+'\"')", source)

    def test_browser_uses_server_filename(self):
        source = inspect.getsource(configurator)
        self.assertIn("response.headers.get('Content-Disposition')", source)
        self.assertIn("link.download=match?match[1]", source)


if __name__ == "__main__":
    unittest.main()
