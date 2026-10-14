import os
import tempfile
import unittest
from pathlib import Path

from universal_led.wifi_worker_deployment import inspect_worker

class WorkerDeploymentTests(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.path=Path(self.temp.name)/'worker'
        self.path.write_text('#!/usr/bin/env python3\n',encoding='utf-8')
        self.path.chmod(0o755)

    def inspect(self):
        return inspect_worker(path=self.path,expected_uid=os.getuid())

    def test_private_executable_is_ready(self):
        self.assertTrue(self.inspect()['ready'])
        self.assertFalse(self.inspect()['network_changed'])

    def test_missing_worker_is_not_ready(self):
        self.path.unlink()
        self.assertEqual(self.inspect()['reason'],'missing')

    def test_nonexecutable_worker_is_not_ready(self):
        self.path.chmod(0o644)
        self.assertFalse(self.inspect()['ready'])

    def test_symlink_worker_is_not_ready(self):
        target=self.path.with_name('target')
        self.path.rename(target)
        self.path.symlink_to(target)
        self.assertEqual(self.inspect()['reason'],'not_regular_file')

    def test_hardlinked_worker_is_not_ready(self):
        os.link(self.path,self.path.with_name('other'))
        self.assertEqual(self.inspect()['reason'],'multiple_links')

    def test_wrong_owner_is_not_ready(self):
        result=inspect_worker(path=self.path,expected_uid=os.getuid()+1)
        self.assertEqual(result['reason'],'wrong_owner')

    def test_directory_is_not_ready(self):
        self.path.unlink()
        self.path.mkdir()
        self.assertEqual(self.inspect()['reason'],'not_regular_file')

if __name__=='__main__':
    unittest.main()
