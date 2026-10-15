"""NetworkManager saved-profile discovery for the Universal Wi-Fi configurator.

Adapted from the existing MLB Configurator's NetworkManager workflow.
Read-only; never prints or retrieves passwords. No elevated privileges.
"""
from __future__ import annotations

import subprocess

from .wifi_diagnostics import _split_nmcli


def saved_wifi_profiles(*, run=subprocess.run):
    """List saved Wi-Fi connections without accessing stored secrets."""
    try:
        result = run(
            ['nmcli', '--terse', '--escape', 'yes', '--fields',
             'NAME,UUID,TYPE,DEVICE', 'connection', 'show'],
            capture_output=True, text=True, timeout=8, check=False,
        )
    except (OSError, subprocess.TimeoutExpired):
        return {'available': False, 'profiles': [], 'error': 'NetworkManager unavailable'}
    if result.returncode:
        return {'available': False, 'profiles': [], 'error': 'Could not list saved connections'}
    profiles = []
    for line in result.stdout.splitlines():
        parts = _split_nmcli(line)
        if len(parts) != 4:
            continue
        name, uuid, kind, device = parts
        if kind not in ('802-11-wireless', 'wifi') or not name or not uuid:
            continue
        # Query only the SSID and mode, never secrets. Profile names may be
        # netplan-wlan0-SSID and therefore cannot be used as SSIDs.
        try:
            details = run(['nmcli', '--get-values',
                           '802-11-wireless.ssid,802-11-wireless.mode',
                           'connection', 'show', 'uuid', uuid],
                          capture_output=True, text=True, timeout=8, check=False)
        except (OSError, subprocess.TimeoutExpired):
            continue
        if details.returncode:
            continue
        values = details.stdout.splitlines()
        if not values or not values[0]:
            continue
        ssid = values[0]
        mode = values[1] if len(values) > 1 else ''
        if mode == 'ap':
            continue
        profiles.append({'name': name, 'ssid': ssid, 'uuid': uuid,
                         'interface': '' if device == '--' else device,
                         'active': device not in ('', '--')})
    return {'available': True, 'profiles': profiles, 'error': None}
