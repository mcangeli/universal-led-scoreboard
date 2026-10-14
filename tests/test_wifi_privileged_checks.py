import importlib.util
import stat
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import Mock

PATH=Path(__file__).resolve().parents[1]/'scripts'/'universal_led_wifi_privileged_checks.py'
spec=importlib.util.spec_from_file_location('privileged_checks',PATH)
checks=importlib.util.module_from_spec(spec)
spec.loader.exec_module(checks)

class PrivilegedReadinessTests(unittest.TestCase):
    def test_worker_permissions(self):
        good=SimpleNamespace(st_mode=stat.S_IFREG|0o755,st_uid=0,st_gid=0)
        self.assertTrue(checks.check_worker(stat_func=lambda *a,**kw:good))
        for mode,uid in ((stat.S_IFREG|0o777,0),(stat.S_IFLNK|0o777,0),
                         (stat.S_IFREG|0o755,1000)):
            with self.subTest(mode=mode,uid=uid):
                info=SimpleNamespace(st_mode=mode,st_uid=uid,st_gid=0)
                self.assertFalse(checks.check_worker(stat_func=lambda *a,**kw:info))

    def test_systemd_status(self):
        for state,expected in [('running',True),('degraded',True),('offline',False)]:
            runner=Mock(return_value=SimpleNamespace(stdout=state,returncode=0))
            self.assertEqual(checks.check_systemd(run=runner),expected)

    def test_readiness_never_arms_or_enables(self):
        result=checks.recovery_status(worker_check=lambda:True,
                                      systemd_check=lambda:True)
        self.assertTrue(result['ok'])
        self.assertFalse(result['rollback_armed'])
        self.assertFalse(result['switching_enabled'])

    def test_failure_is_fail_closed(self):
        result=checks.recovery_status(worker_check=lambda:False,
                                      systemd_check=lambda:True)
        self.assertFalse(result['ok'])
        self.assertFalse(result['switching_enabled'])

if __name__=='__main__':
    unittest.main()
