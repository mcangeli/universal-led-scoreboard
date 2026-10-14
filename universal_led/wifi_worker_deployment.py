"""Read-only deployment checks for the Wi-Fi rollback worker.

No recovery unit is started, no state is armed, and NetworkManager is untouched.
"""
from __future__ import annotations

import os
from pathlib import Path
import stat
import hashlib

WORKER=Path('/usr/local/libexec/universal-led-wifi-recovery')

def inspect_worker(*, path=WORKER, expected_uid=0):
    target=Path(path)
    try:
        info=target.lstat()
    except OSError:
        return {'ready':False,'reason':'missing','path':str(target),
                'network_changed':False}
    if not stat.S_ISREG(info.st_mode):
        reason='not_regular_file'
    elif info.st_uid!=expected_uid:
        reason='wrong_owner'
    elif info.st_nlink!=1:
        reason='multiple_links'
    elif stat.S_IMODE(info.st_mode)!=0o755:
        reason='wrong_mode'
    elif not os.access(target,os.X_OK):
        reason='not_executable'
    else:
        reason=None
    return {'ready':reason is None,'reason':reason,'path':str(target),
            'network_changed':False}

def inspect_source_match(*, installed=WORKER, source=None, expected_uid=0):
    """Read-only content verification; never executes the installed worker."""
    result=inspect_worker(path=installed,expected_uid=expected_uid)
    result['source_matches']=False
    if not result['ready']:
        return result
    if source is None:
        result['ready']=False
        result['reason']='source_not_provided'
        return result
    try:
        source_path=Path(source)
        source_stat=source_path.lstat()
        if not stat.S_ISREG(source_stat.st_mode):
            raise ValueError('invalid_source')
        digest=lambda p: hashlib.sha256(p.read_bytes()).digest()
        result['source_matches']=digest(Path(installed))==digest(source_path)
        if not result['source_matches']:
            result['ready']=False
            result['reason']='content_mismatch'
    except (OSError,ValueError):
        result['ready']=False
        result['reason']='source_unavailable'
    return result
