"""Pure validation for future privileged Wi-Fi connection requests.

No NetworkManager, systemd, filesystem, or subprocess operations are performed.
"""
from __future__ import annotations

from dataclasses import dataclass
import re

from .wifi_recovery import valid_token
from .wifi_recovery_scheduler import validate_target

_ACTIONS = frozenset({'prepare', 'confirm', 'inspect'})
_SAFE_SSID = re.compile(r'^[^\x00-\x1f\x7f]{1,32}$')


@dataclass(frozen=True)
class WifiRequest:
    action: str
    interface: str | None = None
    previous_connection: str | None = None
    target_ssid: str | None = None
    token: str | None = None


def validate_request(payload):
    """Return a normalized immutable request, rejecting unknown fields.

    The request deliberately does not accept passwords or arbitrary command
    arguments. Credentials need a separately designed protected channel.
    """
    if not isinstance(payload, dict):
        raise ValueError('Request must be an object')
    if payload.keys() - {'action', 'interface', 'previous_connection',
                          'target_ssid', 'token'}:
        raise ValueError('Unknown request fields')
    action = payload.get('action')
    if action not in _ACTIONS:
        raise ValueError('Unsupported Wi-Fi action')
    if action == 'prepare':
        if set(payload) != {'action', 'interface', 'previous_connection', 'target_ssid'}:
            raise ValueError('Incomplete preparation request')
        interface = payload['interface']
        previous = payload['previous_connection']
        ssid = payload['target_ssid']
        validate_target(interface, previous)
        if not isinstance(ssid, str) or not _SAFE_SSID.fullmatch(ssid):
            raise ValueError('Invalid target SSID')
        return WifiRequest(action, interface, previous, ssid)
    if set(payload) != {'action', 'token'}:
        raise ValueError('Invalid confirmation or inspection request')
    token = payload['token']
    if not valid_token(token):
        raise ValueError('Invalid recovery token')
    return WifiRequest(action, token=token)
