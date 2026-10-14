"""Read-only privileged helper recovery readiness inspection.

Standalone by design: the installed helper must not depend on the repository
being present or import modules from a user-writable checkout.
"""
from __future__ import annotations
import os
from pathlib import Path
import stat
import subprocess

WORKER = Path('/usr/local/libexec/universal-led-wifi-recovery')

def check_worker(path=WORKER, *, stat_func=os.stat):
    try:
        info=stat_func(path,follow_symlinks=False)
    except OSError:
        return False
    return (stat.S_ISREG(info.st_mode) and info.st_uid==0 and info.st_gid==0
            and not (info.st_mode & 0o022) and bool(info.st_mode & stat.S_IXUSR))

def check_systemd(*, run=subprocess.run):
    try:
        result=run(['systemctl','--system','is-system-running'],
                   capture_output=True,text=True,timeout=8,check=False)
    except (OSError,subprocess.TimeoutExpired):
        return False
    return result.stdout.strip() in ('running','degraded')

def recovery_status(*, worker_check=check_worker, systemd_check=check_systemd):
    worker_ok=worker_check()
    systemd_ok=systemd_check()
    return {'ok':worker_ok and systemd_ok,'operation':'recovery_check',
            'worker_ready':worker_ok,'systemd_ready':systemd_ok,
            'rollback_armed':False,'switching_enabled':False}
