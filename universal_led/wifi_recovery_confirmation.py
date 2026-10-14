"""Privileged confirmation of a pending Wi-Fi rollback.

Cancellation must win the state-file lock before stopping the transient unit.
A worker already executing recovery must never be interrupted by confirmation.
This module does not change NetworkManager connections.
"""
from __future__ import annotations

import os
import subprocess

from .wifi_recovery import valid_token
from .wifi_recovery_cancellation import cancel_recovery
from .wifi_recovery_scheduler import STATE_DIR, UNIT_PREFIX


def confirm_recovery(token, *, state_dir=STATE_DIR, run=subprocess.run,
                     cancel=cancel_recovery, expected_uid=0):
    """Cancel a pending rollback, then request transient-unit shutdown.

    A failed unit stop is reported rather than undoing cancellation: once the
    state is removed, the worker cannot begin a rollback. No stop is issued if
    the state is missing or a rollback has already entered execution.
    """
    if os.geteuid() != expected_uid:
        raise PermissionError('Root required to confirm recovery')
    if not valid_token(token):
        raise ValueError('Invalid recovery token')
    if not cancel(token, state_dir=state_dir):
        return {'confirmed': False, 'reason': 'not_pending', 'unit_stopped': False}
    unit=UNIT_PREFIX + token + '.service'
    try:
        result=run(['systemctl','stop',unit],capture_output=True,text=True,
                   timeout=12,check=False)
    except (OSError,subprocess.TimeoutExpired):
        return {'confirmed': True, 'reason': 'stop_unverified', 'unit_stopped': False}
    if result.returncode:
        return {'confirmed': True, 'reason': 'stop_failed', 'unit_stopped': False}
    return {'confirmed': True, 'reason': 'confirmed', 'unit_stopped': True}
