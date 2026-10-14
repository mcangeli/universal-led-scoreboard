import os
import tempfile
import unittest
from pathlib import Path

from universal_led.wifi_recovery_state_security import verify_state_file

TOKEN='e'*32

class RecoveryStateSecurityTests(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.directory=Path(self.temp.name)/'state'
        self.directory.mkdir(mode=0o700)
        self.path=self.directory/(TOKEN+'.json')
        self.path.write_text('{}',encoding='utf-8')
        self.path.chmod(0o600)

    def verify(self):
        return verify_state_file(TOKEN,state_dir=self.directory,
                                 expected_uid=os.getuid())

    def test_private_state_accepted(self):
        self.assertTrue(self.verify())

    def test_world_readable_state_rejected(self):
        self.path.chmod(0o644)
        self.assertFalse(self.verify())

    def test_insecure_directory_rejected(self):
        self.directory.chmod(0o755)
        self.assertFalse(self.verify())

    def test_symlink_state_rejected(self):
        self.path.unlink()
        target=Path(self.temp.name)/'target'
        target.write_text('{}',encoding='utf-8')
        self.path.symlink_to(target)
        self.assertFalse(self.verify())

    def test_hardlinked_state_rejected(self):
        other=Path(self.temp.name)/'other'
        os.link(self.path,other)
        self.assertFalse(self.verify())

    def test_symlink_directory_rejected(self):
        alias=Path(self.temp.name)/'alias'
        alias.symlink_to(self.directory,target_is_directory=True)
        self.assertFalse(verify_state_file(TOKEN,state_dir=alias,
                                           expected_uid=os.getuid()))

    def test_wrong_owner_rejected(self):
        self.assertFalse(verify_state_file(TOKEN,state_dir=self.directory,
                                           expected_uid=os.getuid()+1))

    def test_missing_state_rejected(self):
        self.path.unlink()
        self.assertFalse(self.verify())

    def test_invalid_token_rejected(self):
        self.assertFalse(verify_state_file('../escape',state_dir=self.directory,
                                           expected_uid=os.getuid()))

if __name__=='__main__':
    unittest.main()
