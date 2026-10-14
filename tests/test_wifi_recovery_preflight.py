import stat
import unittest
from types import SimpleNamespace
from unittest.mock import Mock

from universal_led.wifi_recovery_preflight import (
    verify_worker, verify_systemd, recovery_preflight)

def file_stat(mode=stat.S_IFREG|0o755, uid=0, gid=0):
    return SimpleNamespace(st_mode=mode,st_uid=uid,st_gid=gid)

class WifiRecoveryPreflightTests(unittest.TestCase):
    def test_root_owned_executable_accepted(self):
        self.assertTrue(verify_worker(stat_func=lambda *a,**kw:file_stat())['ready'])

    def test_nonroot_owned_rejected(self):
        self.assertFalse(verify_worker(stat_func=lambda *a,**kw:file_stat(uid=1000))['ready'])

    def test_writable_worker_rejected(self):
        self.assertFalse(verify_worker(stat_func=lambda *a,**kw:file_stat(stat.S_IFREG|0o775))['ready'])

    def test_symlink_rejected(self):
        self.assertFalse(verify_worker(stat_func=lambda *a,**kw:file_stat(stat.S_IFLNK|0o777))['ready'])

    def test_nonexecutable_rejected(self):
        self.assertFalse(verify_worker(stat_func=lambda *a,**kw:file_stat(stat.S_IFREG|0o644))['ready'])

    def test_missing_worker_rejected(self):
        def missing(*a,**kw): raise FileNotFoundError()
        self.assertFalse(verify_worker(stat_func=missing)['ready'])

    def test_running_and_degraded_systemd(self):
        for state in ('running','degraded'):
            with self.subTest(state=state):
                run=Mock(return_value=SimpleNamespace(stdout=state,returncode=0))
                self.assertTrue(verify_systemd(run=run)['ready'])
                self.assertEqual(run.call_args.args[0][:2],['systemctl','--system'])

    def test_offline_systemd_rejected(self):
        run=Mock(return_value=SimpleNamespace(stdout='offline',returncode=1))
        self.assertFalse(verify_systemd(run=run)['ready'])

    def test_preflight_never_enables_switching(self):
        run=Mock(return_value=SimpleNamespace(stdout='running',returncode=0))
        response=recovery_preflight(stat_func=lambda *a,**kw:file_stat(),run=run)
        self.assertTrue(response['ready'])
        self.assertFalse(response['switching_enabled'])
        self.assertFalse(response['rollback_armed'])

if __name__=='__main__':
    unittest.main()
