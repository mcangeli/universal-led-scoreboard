"""Verify independent rollback worker startup before authorizing any switch.

This wrapper does not change Wi-Fi, cancel recovery, or remove recovery state.
If verification fails, the scheduled worker is left intact to fail safely.
"""
from __future__ import annotations
import time

from .wifi_recovery_scheduler import arm_recovery, recovery_pending
from .wifi_recovery_lifecycle import inspect_recovery_unit

def arm_and_verify(interface, previous_connection, *, arm=arm_recovery,
                   inspect=inspect_recovery_unit, pending=recovery_pending,
                   sleep=time.sleep, attempts=5, interval=0.2):
    if not isinstance(attempts,int) or not 1 <= attempts <= 20:
        raise ValueError('Invalid verification attempts')
    if not isinstance(interval,(int,float)) or not 0 <= interval <= 2:
        raise ValueError('Invalid verification interval')
    token=arm(interface,previous_connection)
    for attempt in range(attempts):
        if not pending(token):
            raise RuntimeError('Recovery state disappeared before verification')
        status=inspect(token)
        if status.get('armed') is True:
            if not pending(token):
                raise RuntimeError('Recovery state disappeared during verification')
            return token
        if attempt+1 < attempts:
            sleep(interval)
    raise RuntimeError('Recovery worker did not become active; Wi-Fi switch prohibited')
