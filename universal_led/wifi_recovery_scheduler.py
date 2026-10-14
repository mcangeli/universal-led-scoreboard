"""Root-only rollback arming for NetworkManager changes.

No connection switching is performed here. A rollback must be independently
scheduled before a future connection helper may alter Wi-Fi.
"""
from __future__ import annotations

import json
import os
from pathlib import Path
import re
import secrets
import subprocess

STATE_DIR = Path('/run/universal-led-scoreboard/wifi-recovery')
INTERFACE = re.compile(r'^wl[a-zA-Z0-9_.-]{1,30}$')
UNIT_PREFIX = 'universal-led-wifi-recovery-'

def validate_target(interface, previous_connection):
    if not isinstance(interface, str) or not INTERFACE.fullmatch(interface):
        raise ValueError('Invalid wireless interface')
    if (not isinstance(previous_connection, str) or not previous_connection
            or len(previous_connection) > 128 or any(ord(c) < 32 for c in previous_connection)):
        raise ValueError('Invalid previous connection')

def arm_recovery(interface, previous_connection, *, state_dir=STATE_DIR,
                 run=subprocess.run, token_factory=lambda: secrets.token_hex(16),
                 recovery_script='/usr/local/libexec/universal-led-wifi-recovery'):
    """Create private state and start a root systemd worker, or fail closed.

    The worker must be installed root-owned. systemd-run returns only after
    the transient unit has been accepted, not after its timer expires.
    """
    if os.geteuid() != 0:
        raise PermissionError('Root required')
    validate_target(interface, previous_connection)
    token=token_factory()
    if not re.fullmatch(r'[0-9a-f]{32}', token):
        raise ValueError('Invalid recovery token')
    state_dir.mkdir(mode=0o700, parents=True, exist_ok=True)
    if state_dir.is_symlink() or state_dir.stat().st_uid != 0:
        raise PermissionError('Recovery directory must be root-owned')
    os.chmod(state_dir, 0o700)
    path=state_dir/(token+'.json')
    payload={'token':token,'interface':interface,
             'previous_connection':previous_connection,'delay':90}
    fd=os.open(path, os.O_WRONLY | os.O_CREAT | os.O_EXCL | getattr(os,'O_NOFOLLOW',0),0o600)
    try:
        with os.fdopen(fd,'w',encoding='utf-8') as handle:
            json.dump(payload,handle)
        result=run(['systemd-run','--system','--quiet','--collect',
                    '--unit='+UNIT_PREFIX+token,
                    '--property=User=root',
                    '--property=Type=exec',
                    recovery_script,token],
                   capture_output=True,text=True,timeout=12,check=False)
        if result.returncode:
            raise RuntimeError('Could not schedule Wi-Fi recovery')
        return token
    except BaseException:
        path.unlink(missing_ok=True)
        raise

def recovery_pending(token, *, state_dir=STATE_DIR):
    if not re.fullmatch(r'[0-9a-f]{32}',token):
        return False
    return (state_dir/(token+'.json')).is_file()
