import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch
from universal_led.configurator import persistent_form_token

class PersistentFormTokenTests(unittest.TestCase):
    def test_survives_repeated_calls_and_restarts(self):
        with tempfile.TemporaryDirectory() as directory:
            first = persistent_form_token(directory)
            self.assertGreaterEqual(len(first), 32)
            self.assertEqual(persistent_form_token(directory), first)
            self.assertEqual((Path(directory) / 'form_token').read_text().strip(), first)

    def test_file_permissions_are_private(self):
        with tempfile.TemporaryDirectory() as directory:
            persistent_form_token(directory)
            self.assertEqual((Path(directory) / 'form_token').stat().st_mode & 0o777, 0o600)

if __name__ == '__main__':
    unittest.main()
