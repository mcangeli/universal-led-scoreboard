import os
import tempfile
import unittest
from pathlib import Path

from universal_led.wifi_recovery_safe_file import open_state, same_state

class SafeStateFileTests(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.path=Path(self.temp.name)/('a'*32+'.json')
        self.path.write_text('{}',encoding='utf-8')
        self.path.chmod(0o600)

    def test_private_regular_file(self):
        with open_state(self.path,expected_uid=os.getuid()) as handle:
            self.assertTrue(same_state(self.path,handle))

    def test_replaced_file_is_not_same_state(self):
        with open_state(self.path) as handle:
            self.path.unlink()
            self.path.write_text('{}',encoding='utf-8')
            self.path.chmod(0o600)
            self.assertFalse(same_state(self.path,handle))

    def test_symlink_is_rejected(self):
        alias=Path(self.temp.name)/'alias'
        alias.symlink_to(self.path)
        with self.assertRaises(OSError):
            open_state(alias)

    def test_insecure_permissions_rejected(self):
        self.path.chmod(0o644)
        with self.assertRaises(PermissionError):
            open_state(self.path)

    def test_hardlink_rejected(self):
        os.link(self.path,Path(self.temp.name)/'other')
        with self.assertRaises(PermissionError):
            open_state(self.path)

    def test_wrong_owner_rejected(self):
        with self.assertRaises(PermissionError):
            open_state(self.path,expected_uid=os.getuid()+1)

if __name__=='__main__':
    unittest.main()
