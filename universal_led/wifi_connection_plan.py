"""Pure planning and verification for guarded NetworkManager connection changes.

Adapted from the existing MLB Scoreboard Configurator's network workflow.
This module deliberately performs no privileged operations or secret handling.
"""
from __future__ import annotations
from dataclasses import dataclass
from .wifi_provisioning import validate_connection_request

@dataclass(frozen=True)
class ConnectionPlan:
    ssid: str
    security: str
    interface: str
    previous_connection: str
    rollback_required: bool = True

def plan_connection(data, status):
    """Require an identifiable current client connection before changing Wi-Fi."""
    validated = validate_connection_request(data)
    if not status.get('available'):
        raise ValueError('NetworkManager unavailable')
    connected = [d for d in status.get('devices', [])
                 if d.get('state') == 'connected' and d.get('device')
                 and d.get('connection')]
    if len(connected) != 1:
        raise ValueError('Exactly one active Wi-Fi connection is required for safe switching')
    current = connected[0]
    if current['connection'] == validated['ssid']:
        raise ValueError('Already connected to this network')
    return ConnectionPlan(ssid=validated['ssid'], security=validated['security'],
                          interface=current['device'],
                          previous_connection=current['connection'])

def rollback_commands(plan):
    """Return the recovery action; actual execution belongs to a root-owned helper."""
    if not isinstance(plan, ConnectionPlan) or not plan.rollback_required:
        raise ValueError('Rollback plan required')
    return [['nmcli', 'connection', 'up', 'id', plan.previous_connection,
             'ifname', plan.interface]]

def verify_connection(plan, status):
    """Verify that the intended client connection is active on the original device."""
    return bool(status.get('available') and any(
        d.get('device') == plan.interface and d.get('state') == 'connected'
        and d.get('connection') == plan.ssid for d in status.get('devices', [])))
