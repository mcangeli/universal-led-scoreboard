"""Validate private recovery-state files without following symbolic links."""
from __future__ import annotations

import os
import stat
from pathlib import Path

from .wifi_recovery import valid_token

def verify_state_file(token, *, state_dir, expected_uid=0):
    if not valid_token(token):
        return False
    directory=Path(state_dir)
    try:
        dstat=directory.lstat()
        if not stat.S_ISDIR(dstat.st_mode) or dstat.st_uid!=expected_uid:
            return False
        if stat.S_IMODE(dstat.st_mode)!=0o700:
            return False
        path=directory/(token+'.json')
        info=path.lstat()
        if not stat.S_ISREG(info.st_mode) or info.st_uid!=expected_uid:
            return False
        if stat.S_IMODE(info.st_mode)!=0o600 or info.st_nlink!=1:
            return False
        return True
    except (FileNotFoundError,NotADirectoryError,PermissionError):
        return False
