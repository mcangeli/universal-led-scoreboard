"""Bridge verified systemd recovery to the guarded switch transaction.

This module is intentionally non-mutating. No Wi-Fi connection is changed.
"""
from __future__ import annotations

from .wifi_connection_plan import plan_connection
from .wifi_switch_transaction import SwitchTransaction
from .wifi_verified_recovery import arm_and_verify
from .wifi_recovery_lifecycle import inspect_recovery_unit
from .wifi_recovery_scheduler import recovery_pending

def prepare_verified_switch(request,status,*,arm=arm_and_verify):
    plan=plan_connection(request,status)
    token=arm(plan.interface,plan.previous_connection)
    return SwitchTransaction(plan.previous_connection,plan.interface,plan.ssid).transition(
        'arm',recovery_token=token)

def require_verified_switch(transaction,*,inspect=inspect_recovery_unit,
                            pending=recovery_pending):
    if not transaction.may_change_network:
        raise RuntimeError('Wi-Fi switch not authorized')
    if not pending(transaction.recovery_token):
        raise RuntimeError('Recovery state missing; Wi-Fi switch denied')
    result=inspect(transaction.recovery_token)
    if not isinstance(result,dict) or result.get('armed') is not True:
        raise RuntimeError('Recovery worker not running; Wi-Fi switch denied')
    return True
