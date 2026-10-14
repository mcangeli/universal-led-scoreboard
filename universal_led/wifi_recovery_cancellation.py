"""Serialize recovery execution and cancellation with an advisory state-file lock.

The caller must be privileged and the state directory must be private.
A cancellation that wins the lock prevents rollback; one arriving after
rollback begins fails immediately and reports that it was too late.
"""
from __future__ import annotations
import fcntl
import os
import json
from pathlib import Path

from .wifi_recovery import valid_token
from .wifi_recovery_safe_file import open_state, same_state

def cancel_recovery(token, *, state_dir):
    if not valid_token(token):
        raise ValueError('Invalid recovery token')
    path=Path(state_dir)/(token+'.json')
    try:
        with open_state(path) as handle:
            try:
                fcntl.flock(handle.fileno(),fcntl.LOCK_EX | fcntl.LOCK_NB)
            except BlockingIOError:
                return False
            try:
                data=json.load(handle)
                if data.get('token')!=token:
                    raise ValueError('Recovery token mismatch')
                if not same_state(path,handle):
                    return False
                if data.get('phase')=='executing':
                    return False
                path.unlink()
                return True
            finally:
                fcntl.flock(handle.fileno(),fcntl.LOCK_UN)
    except FileNotFoundError:
        return False
