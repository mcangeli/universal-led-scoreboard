"""Privileged Wi-Fi switch transaction, reusing MLB configurator nmcli behavior.

This module is deliberately not a web route or sudo entrypoint. The caller must
enforce authorization and provide a verified rollback installation first.
"""
from __future__ import annotations

import os
import subprocess

from .wifi_recovery_scheduler import arm_recovery, validate_target
from .wifi_connection_request import validate_request


def switch_saved_profile(interface, previous_connection, target_ssid, profile_uuid, *,
                         arm=arm_recovery, run=subprocess.run):
    """Arm rollback before activating an existing saved NetworkManager profile.

    No passwords or shell commands are accepted. On connection failure the
    recovery worker remains armed; it must not be cancelled optimistically.
    """
    if os.geteuid() != 0:
        raise PermissionError('Root required')
    validate_request({'action': 'prepare', 'interface': interface,
                      'previous_connection': previous_connection,
                      'target_ssid': target_ssid})
    import uuid
    try:
        canonical = str(uuid.UUID(profile_uuid))
    except (ValueError, TypeError, AttributeError):
        raise ValueError('Invalid saved profile UUID') from None
    if canonical != profile_uuid:
        raise ValueError('Noncanonical saved profile UUID')
    token = arm(interface, previous_connection)
    try:
        result = run(['nmcli', '--wait', '45', 'connection', 'up',
                      'uuid', canonical, 'ifname', interface],
                     capture_output=True, text=True, timeout=55, check=False)
        success = result.returncode == 0
    except (OSError, subprocess.TimeoutExpired):
        success = False
    return {'started': success, 'recovery_token': token,
            'confirmation_required': True,
            'message': 'Connection activation requested' if success
                       else 'Connection failed; automatic recovery remains armed'}
