import os
import tempfile
import unittest
from pathlib import Path
from universal_led.wifi_deployment_preflight import deployment_preflight

class DeploymentPreflightTests(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        base=Path(self.temp.name)
        self.source=base/'source.py'
        self.installed=base/'installed'
        for path in (self.source,self.installed):
            path.write_text('#!/usr/bin/env python3\npass\n')
            path.chmod(0o755)

    def check(self,which=lambda name:'/usr/bin/'+name):
        return deployment_preflight(source=self.source,installed=self.installed,
                                    expected_uid=os.getuid(),which=which)

    def test_complete_environment_is_ready(self):
        result=self.check()
        self.assertTrue(result['ready'])
        self.assertFalse(result['network_changed'])
        self.assertFalse(result['worker_started'])

    def test_missing_systemd_run_fails_closed(self):
        result=self.check(which=lambda name:None if name=='systemd-run' else '/usr/bin/'+name)
        self.assertFalse(result['ready'])
        self.assertFalse(result['checks']['systemd_run_available'])

    def test_missing_nmcli_fails_closed(self):
        result=self.check(which=lambda name:None if name=='nmcli' else '/usr/bin/'+name)
        self.assertFalse(result['ready'])

    def test_mismatched_worker_fails_closed(self):
        self.installed.write_text('tampered')
        self.assertEqual(self.check()['worker_reason'],'content_mismatch')

    def test_missing_source_fails_closed(self):
        self.source.unlink()
        self.assertFalse(self.check()['ready'])

    def test_symlink_source_fails_closed(self):
        target=self.source.with_name('target')
        self.source.rename(target)
        self.source.symlink_to(target)
        self.assertFalse(self.check()['checks']['source_regular'])

    def test_missing_worker_fails_closed(self):
        self.installed.unlink()
        self.assertFalse(self.check()['ready'])

if __name__=='__main__':
    unittest.main()
