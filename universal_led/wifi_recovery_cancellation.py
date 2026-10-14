"""Serialize recovery execution and cancellation with an advisory state-file lock.

The caller must be privileged and the state directory must be private.
A cancellation that wins the lock prevents rollback; one arriving after
rollback begins waits until it finishes and reports that it was too late.
"""
from __future__ import annotations
import fcntl
import json
from pathlib import Path

from .wifi_recovery import valid_token

def cancel_recovery(token, *, state_dir):
    if not valid_token(token):
        raise ValueError('Invalid recovery token')
    path=Path(state_dir)/(token+'.json')
    try:
        with path.open('r+',encoding='utf-8') as handle:
            fcntl.flock(handle.fileno(),fcntl.LOCK_EX)
            try:
                data=json.load(handle)
                if data.get('token')!=token:
                    raise ValueError('Recovery token mismatch')
                if not path.exists() or path.stat().st_ino!=__import__('os').fstat(handle.fileno()).st_ino:
                    return False
                if data.get('phase')=='executing':
                    return False
                path.unlink()
                return True
            finally:
                fcntl.flock(handle.fileno(),fcntl.LOCK_UN)
    except FileNotFoundError:
        return False
