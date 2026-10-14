"""Read-only checks before allowing the privileged recovery scheduler to arm.

Never starts a systemd unit or modifies a network connection.
"""
from __future__ import annotations

from pathlib import Path
import os
import stat
import subprocess

RECOVERY_WORKER = Path('/usr/local/libexec/universal-led-wifi-recovery')

def verify_worker(path=RECOVERY_WORKER, *, stat_func=os.stat):
    """Reject symlinks, writable or non-root-owned recovery executables."""
    try:
        info=stat_func(path, follow_symlinks=False)
    except OSError:
        return {'ready':False,'reason':'Recovery worker missing'}
    if not stat.S_ISREG(info.st_mode):
        return {'ready':False,'reason':'Recovery worker is not a regular file'}
    if info.st_uid != 0 or info.st_gid != 0:
        return {'ready':False,'reason':'Recovery worker must be owned by root'}
    if info.st_mode & 0o022:
        return {'ready':False,'reason':'Recovery worker is writable by non-root users'}
    if not info.st_mode & stat.S_IXUSR:
        return {'ready':False,'reason':'Recovery worker is not executable'}
    return {'ready':True,'reason':'Recovery worker permissions verified'}

def verify_systemd(*, run=subprocess.run):
    """Only checks availability, never launches a recovery worker."""
    try:
        result=run(['systemctl','--system','is-system-running'],
                   capture_output=True,text=True,timeout=8,check=False)
    except (OSError,subprocess.TimeoutExpired):
        return {'ready':False,'reason':'System systemd unavailable'}
    # 'degraded' is common on Pi hosts with unrelated service failures.
    state=result.stdout.strip()
    if state not in ('running','degraded'):
        return {'ready':False,'reason':'System systemd is not ready'}
    return {'ready':True,'reason':'System systemd available'}

def recovery_preflight(*, worker=RECOVERY_WORKER, stat_func=os.stat,
                       run=subprocess.run):
    checks=[verify_worker(worker,stat_func=stat_func),
            verify_systemd(run=run)]
    return {'ready':all(item['ready'] for item in checks),
            'checks':checks,'switching_enabled':False,'rollback_armed':False}

def main():
    import json
    print(json.dumps(recovery_preflight(),separators=(',',':')))

if __name__ == '__main__':
    main()
