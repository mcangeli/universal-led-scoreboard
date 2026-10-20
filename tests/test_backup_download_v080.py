"""Dashboard portable backup download integration."""
import inspect
import unittest
from universal_led import configurator


class BackupDownloadTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.source = inspect.getsource(configurator)

    def test_dashboard_exposes_download_button(self):
        self.assertIn('id="download-backup"', self.source)
        self.assertIn('onclick="downloadBackup()"', self.source)
        self.assertIn("fetch('/api/backup/export'", self.source)

    def test_backup_is_authenticated_and_attachment(self):
        source = self.source
        self.assertLess(source.index("if not self.authenticated():"), source.index("elif path=='/api/backup/export':"))
        self.assertIn("body=export_portable(config_dir)", source)
        self.assertIn("self.send_header('Content-Type','application/zip')", source)
        self.assertIn("self.send_header('Content-Disposition','attachment;", source)


if __name__ == '__main__':
    unittest.main()
