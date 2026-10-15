"""Root-owned, locked, durable Wi-Fi switch reservations.

This module never changes NetworkManager or schedules recovery workers.
The lock is held only while inspecting/updating reservations. The privileged
helper must also coordinate actual switching and rollback with this state.
"""
from __future__ import annotations

import fcntl
import json
import os
from pathlib import Path
import stat

from .wifi_recovery import valid_token
from .wifi_recovery_scheduler import validate_target

DEFAULT_DIR = Path('/run/universal-led-scoreboard/wifi-switches')


def _directory(directory):
    path = Path(directory)
    info = path.lstat()
    if not stat.S_ISDIR(info.st_mode) or info.st_uid != 0 or stat.S_IMODE(info.st_mode) != 0o700:
        raise PermissionError('Switch directory must be root-owned mode 0700')
    return path


def _lock(directory):
    path = _directory(directory) / '.lock'
    fd = os.open(path, os.O_CREAT | os.O_RDWR | getattr(os, 'O_NOFOLLOW', 0), 0o600)
    try:
        info = os.fstat(fd)
        if not stat.S_ISREG(info.st_mode) or info.st_uid != 0 or stat.S_IMODE(info.st_mode) != 0o600 or info.st_nlink != 1:
            raise PermissionError('Invalid switch lock')
        fcntl.flock(fd, fcntl.LOCK_EX)
        return fd
    except BaseException:
        os.close(fd)
        raise


def _entries(directory):
    result = []
    for path in directory.iterdir():
        if path.name == '.lock':
            continue
        if not path.name.endswith('.json') or not valid_token(path.stem):
            raise ValueError('Unexpected switch state entry')
        fd = os.open(path, os.O_RDONLY | getattr(os, 'O_NOFOLLOW', 0))
        try:
            info = os.fstat(fd)
            if not stat.S_ISREG(info.st_mode) or info.st_uid != 0 or stat.S_IMODE(info.st_mode) != 0o600 or info.st_nlink != 1:
                raise PermissionError('Invalid switch state file')
            with os.fdopen(fd, 'r', encoding='utf-8') as handle:
                fd = -1
                data = json.load(handle)
        finally:
            if fd >= 0:
                os.close(fd)
        if data.get('token') != path.stem or data.get('phase') not in ('pending', 'expired', 'confirmed', 'rolled_back'):
            raise ValueError('Invalid switch state')
        validate_target(data.get('interface'), data.get('previous_connection'))
        result.append(data)
    return result


def reserve_switch(interface, previous_connection, token, *, directory=DEFAULT_DIR):
    """Atomically reserve one unresolved switch per interface.

    The directory must already exist, with root ownership and mode 0700.
    """
    if os.geteuid() != 0:
        raise PermissionError('Root required')
    validate_target(interface, previous_connection)
    if not valid_token(token):
        raise ValueError('Invalid recovery token')
    root = _directory(directory)
    fd = _lock(root)
    try:
        entries = _entries(root)
        if any(item['token'] == token for item in entries):
            raise ValueError('Duplicate recovery token')
        if any(item['interface'] == interface and item['phase'] in ('pending', 'expired') for item in entries):
            raise ValueError('Interface already has unresolved switch')
        path = root / (token + '.json')
        payload = {'token': token, 'interface': interface,
                   'previous_connection': previous_connection, 'phase': 'pending'}
        new_fd = os.open(path, os.O_CREAT | os.O_EXCL | os.O_WRONLY | getattr(os, 'O_NOFOLLOW', 0), 0o600)
        with os.fdopen(new_fd, 'w', encoding='utf-8') as handle:
            json.dump(payload, handle)
            handle.flush()
            os.fsync(handle.fileno())
        return payload.copy()
    finally:
        os.close(fd)


def resolve_switch(token, phase, *, directory=DEFAULT_DIR):
    """Resolve a reservation; never treat expiry as successful confirmation."""
    if os.geteuid() != 0:
        raise PermissionError('Root required')
    if not valid_token(token) or phase not in ('confirmed', 'rolled_back', 'expired'):
        raise ValueError('Invalid switch resolution')
    root = _directory(directory)
    fd = _lock(root)
    try:
        entries = _entries(root)
        entry = next((item for item in entries if item['token'] == token), None)
        if entry is None:
            raise ValueError('Unknown recovery token')
        if entry['phase'] not in ('pending', 'expired') or (entry['phase'] == 'expired' and phase == 'confirmed'):
            raise ValueError('Switch cannot transition to requested phase')
        path = root / (token + '.json')
        updated = dict(entry, phase=phase)
        temp = root / ('.' + token + '.tmp')
        new_fd = os.open(temp, os.O_CREAT | os.O_EXCL | os.O_WRONLY | getattr(os, 'O_NOFOLLOW', 0), 0o600)
        try:
            with os.fdopen(new_fd, 'w', encoding='utf-8') as handle:
                json.dump(updated, handle)
                handle.flush()
                os.fsync(handle.fileno())
            os.replace(temp, path)
        finally:
            temp.unlink(missing_ok=True)
        return updated.copy()
    finally:
        os.close(fd)
