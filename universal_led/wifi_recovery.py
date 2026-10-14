#!/usr/bin/env python3
"""Privileged Wi-Fi recovery worker.

Run only from a root-owned systemd transient unit. This process must survive
web service restarts and never receives or logs a Wi-Fi password.
"""
from __future__ import annotations

import argparse
import fcntl
import json
import os
from pathlib import Path
import subprocess
import time

STATE_DIR=Path('/run/universal-led-scoreboard/wifi-recovery')

def valid_token(token):
    return isinstance(token,str) and len(token)==32 and all(c in '0123456789abcdef' for c in token)

def recover(token, *, state_dir=STATE_DIR, sleep=time.sleep, run=subprocess.run):
    if not valid_token(token):
        raise ValueError('Invalid recovery token')
    path=state_dir/(token+'.json')
    # State files are root-owned, created with O_EXCL and mode 0600.
    try:
        with path.open(encoding='utf-8') as handle:
            data=json.load(handle)
    except FileNotFoundError:
        # Confirmation may remove the state before this worker starts.
        # A missing state is a cancelled recovery, not a worker failure.
        return False
    if data.get('token')!=token or not isinstance(data.get('previous_connection'),str) or not isinstance(data.get('interface'),str):
        raise ValueError('Invalid recovery state')
    if not data['previous_connection'] or not data['interface'].startswith('wl'):
        raise ValueError('Invalid recovery target')
    delay=max(0,min(180,int(data.get('delay',90))))
    sleep(delay)
    # Serialize cancellation and rollback. Holding the lock through nmcli
    # prevents confirmation from deleting state during an in-flight rollback.
    try:
        with path.open('r+',encoding='utf-8') as handle:
            fcntl.flock(handle.fileno(),fcntl.LOCK_EX)
            try:
                if not path.exists() or path.stat().st_ino != os.fstat(handle.fileno()).st_ino:
                    return False
                current=json.load(handle)
                if current != data:
                    raise ValueError('Recovery state changed')
                current['phase']='executing'
                handle.seek(0)
                json.dump(current,handle)
                handle.truncate()
                handle.flush()
                os.fsync(handle.fileno())
                result=run(['nmcli','connection','up','id',data['previous_connection'],
                            'ifname',data['interface']],timeout=45,check=False,
                           capture_output=True,text=True)
                if result.returncode != 0:
                    return False
                path.unlink(missing_ok=True)
                return True
            finally:
                fcntl.flock(handle.fileno(),fcntl.LOCK_UN)
    except FileNotFoundError:
        return False

def run_privileged_recovery(token, *, state_dir=STATE_DIR,
                            verify=None, worker=None):
    """Fail closed on unsafe state before entering the recovery worker.

    Dependency injection is limited to isolated regression tests. The actual
    CLI uses the root-owned state directory and the real recovery function.
    """
    from .wifi_recovery_state_security import verify_state_file
    verifier=verify if verify is not None else verify_state_file
    executor=worker if worker is not None else recover
    if os.geteuid()!=0:
        raise PermissionError('Recovery must run as root')
    if not valid_token(token):
        raise ValueError('Invalid recovery token')
    if not verifier(token,state_dir=state_dir,expected_uid=0):
        raise PermissionError('Recovery state is missing or insecure')
    return executor(token,state_dir=state_dir)


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('token')
    args=parser.parse_args()
    if os.geteuid()!=0:
        parser.error('Recovery must run as root')
    run_privileged_recovery(args.token)

if __name__=='__main__':
    main()
