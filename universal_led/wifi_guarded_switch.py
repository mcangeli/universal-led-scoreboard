"""Fail-closed connection preparation used by the future privileged helper.

No Wi-Fi commands are executed here. Preparation validates the active client,
arms independent recovery, and produces an authorized transaction. The caller
must separately check the systemd unit is active before any actual switch.
"""
from __future__ import annotations

from .wifi_connection_plan import plan_connection
from .wifi_switch_transaction import SwitchTransaction

def prepare_guarded_switch(request, status, *, arm, is_armed):
    """Return an armed transaction, never a network-mutating command."""
    plan = plan_connection(request, status)
    tx = SwitchTransaction(previous_connection=plan.previous_connection,
                           interface=plan.interface, target_ssid=plan.ssid)
    token = arm(plan.interface, plan.previous_connection)
    if not is_armed(token):
        raise RuntimeError('Independent recovery is not armed')
    return tx.transition('arm', recovery_token=token)

def require_recovery_before_switch(transaction, *, is_armed):
    """Check protection immediately before any future network modification."""
    if not transaction.may_change_network or not is_armed(transaction.recovery_token):
        raise RuntimeError('Wi-Fi switch denied: rollback is not armed')
    return True
