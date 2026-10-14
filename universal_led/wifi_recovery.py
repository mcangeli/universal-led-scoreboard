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
import stat
from pathlib import Path
import subprocess
import time

STATE_DIR=Path('/run/universal-led-scoreboard/wifi-recovery')

def valid_token(token):
    return isinstance(token,str) and len(token)==32 and all(c in '0123456789abcdef' for c in token)

def secure_open_state(path):
    """Validate the actual opened file, not just its pathname."""
    flags=os.O_RDWR | getattr(os,'O_NOFOLLOW',0) | getattr(os,'O_CLOEXEC',0)
    fd=os.open(path,flags)
    try:
        opened=os.fstat(fd)
        named=path.lstat()
        if (not stat.S_ISREG(opened.st_mode)
                or stat.S_IMODE(opened.st_mode)!=0o600
                or opened.st_nlink!=1 or opened.st_uid!=os.geteuid()
                or (opened.st_dev,opened.st_ino)!=(named.st_dev,named.st_ino)):
            raise PermissionError('Unsafe recovery state file')
        return os.fdopen(fd,'r+',encoding='utf-8')
    except BaseException:
        os.close(fd)
        raise


def _same_open_state(path, handle):
    try:
        named=path.lstat()
        opened=os.fstat(handle.fileno())
        return (named.st_dev,named.st_ino)==(opened.st_dev,opened.st_ino)
    except FileNotFoundError:
        return False


def recover(token, *, state_dir=STATE_DIR, sleep=time.sleep, run=subprocess.run):
    if not valid_token(token):
        raise ValueError('Invalid recovery token')
    path=state_dir/(token+'.json')
    # State files are root-owned, created with O_EXCL and mode 0600.
    try:
        with secure_open_state(path) as handle:
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
        with secure_open_state(path) as handle:
            fcntl.flock(handle.fileno(),fcntl.LOCK_EX)
            try:
                if not _same_open_state(path,handle):
                    return False
                current=json.load(handle)
                if current.get('phase') is not None:
                    return False
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
                if _same_open_state(path,handle):
                    path.unlink()
                return True
            finally:
                fcntl.flock(handle.fileno(),fcntl.LOCK_UN)
    except FileNotFoundError:
        return False

def verify_privileged_state(token, *, state_dir, expected_uid=0):
    """Standalone-safe state checks; worker is installed as a single script."""
    if not valid_token(token):
        return False
    directory=Path(state_dir)
    try:
        dstat=directory.lstat()
        fstat=(directory/(token+'.json')).lstat()
    except (OSError,ValueError):
        return False
    return (stat.S_ISDIR(dstat.st_mode) and dstat.st_uid==expected_uid
            and stat.S_IMODE(dstat.st_mode)==0o700
            and stat.S_ISREG(fstat.st_mode) and fstat.st_uid==expected_uid
            and stat.S_IMODE(fstat.st_mode)==0o600 and fstat.st_nlink==1)


def run_privileged_recovery(token, *, state_dir=STATE_DIR,
                            verify=None, worker=None):
    """Fail closed on unsafe state before entering the recovery worker.

    Dependency injection is limited to isolated regression tests. The actual
    CLI uses the root-owned state directory and the real recovery function.
    """
    verifier=verify if verify is not None else verify_privileged_state
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
