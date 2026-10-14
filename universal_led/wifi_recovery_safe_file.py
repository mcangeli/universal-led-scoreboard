"""Open recovery state without following symlinks, validating the opened inode."""
from __future__ import annotations
import os
import stat
from pathlib import Path

def open_state(path, *, expected_uid=None):
    path=Path(path)
    flags=os.O_RDWR | getattr(os,'O_NOFOLLOW',0) | getattr(os,'O_CLOEXEC',0)
    fd=os.open(path,flags)
    try:
        info=os.fstat(fd)
        if not stat.S_ISREG(info.st_mode) or stat.S_IMODE(info.st_mode)!=0o600 or info.st_nlink!=1:
            raise PermissionError('Unsafe recovery state file')
        if expected_uid is not None and info.st_uid!=expected_uid:
            raise PermissionError('Wrong recovery state owner')
        named=path.lstat()
        if named.st_dev!=info.st_dev or named.st_ino!=info.st_ino:
            raise PermissionError('Recovery state replaced')
        return os.fdopen(fd,'r+',encoding='utf-8')
    except BaseException:
        os.close(fd)
        raise

def same_state(path, handle):
    try:
        named=Path(path).lstat()
        opened=os.fstat(handle.fileno())
        return (named.st_dev,named.st_ino)==(opened.st_dev,opened.st_ino)
    except FileNotFoundError:
        return False
