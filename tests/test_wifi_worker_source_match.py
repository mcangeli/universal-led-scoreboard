import os
import tempfile
import unittest
from pathlib import Path
from universal_led.wifi_worker_deployment import inspect_source_match

class WorkerSourceMatchTests(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        base=Path(self.temp.name)
        self.source=base/'source.py'
        self.installed=base/'installed'
        for p in (self.source,self.installed):
            p.write_text('#!/usr/bin/env python3\nprint("test")\n')
            p.chmod(0o755)

    def inspect(self,**kwargs):
        return inspect_source_match(installed=self.installed,source=self.source,
                                    expected_uid=os.getuid(),**kwargs)

    def test_matching_source_is_ready(self):
        result=self.inspect()
        self.assertTrue(result['ready'])
        self.assertTrue(result['source_matches'])
        self.assertFalse(result['network_changed'])

    def test_modified_installed_worker_is_rejected(self):
        self.installed.write_text('different')
        self.assertEqual(self.inspect()['reason'],'content_mismatch')

    def test_missing_source_is_rejected(self):
        self.source.unlink()
        self.assertEqual(self.inspect()['reason'],'source_unavailable')

    def test_missing_installed_worker_is_rejected(self):
        self.installed.unlink()
        self.assertEqual(self.inspect()['reason'],'missing')

    def test_source_directory_is_rejected(self):
        self.source.unlink()
        self.source.mkdir()
        self.assertEqual(self.inspect()['reason'],'source_unavailable')

    def test_missing_source_argument_fails_closed(self):
        result=inspect_source_match(installed=self.installed,
                                    expected_uid=os.getuid())
        self.assertEqual(result['reason'],'source_not_provided')

if __name__=='__main__':
    unittest.main()
