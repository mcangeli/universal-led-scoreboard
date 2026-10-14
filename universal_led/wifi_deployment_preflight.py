"""Read-only prerequisites for a future privileged recovery deployment.

This never installs files, starts systemd units, or invokes NetworkManager.
"""
from __future__ import annotations

import os
from pathlib import Path
import shutil
import stat

from .wifi_worker_deployment import inspect_source_match

def deployment_preflight(*, source=None, installed=None, expected_uid=0,
                         which=shutil.which):
    """Report deployment prerequisites without changing the host."""
    from .wifi_worker_deployment import WORKER
    source=Path(source) if source is not None else Path(__file__).with_name('wifi_recovery.py')
    installed=Path(installed) if installed is not None else WORKER
    checks={}
    try:
        info=source.lstat()
        checks['source_regular']=stat.S_ISREG(info.st_mode) and info.st_nlink==1
    except OSError:
        checks['source_regular']=False
    checks['python3_available']=bool(which('python3'))
    checks['systemd_run_available']=bool(which('systemd-run'))
    checks['systemctl_available']=bool(which('systemctl'))
    checks['nmcli_available']=bool(which('nmcli'))
    worker=inspect_source_match(installed=installed,source=source,
                                expected_uid=expected_uid)
    checks['worker_verified']=worker['ready'] and worker['source_matches']
    return {'ready':all(checks.values()),'checks':checks,
            'worker_reason':worker['reason'],
            'network_changed':False,'worker_started':False}
