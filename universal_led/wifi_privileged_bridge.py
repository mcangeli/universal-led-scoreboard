#!/usr/bin/env python3
"""Narrow privileged NetworkManager bridge. JSON via stdin; never argv secrets."""
import json
import os
import re
import subprocess
import sys

UUID = re.compile(r'^[0-9a-f]{8}-(?:[0-9a-f]{4}-){3}[0-9a-f]{12}$')
IFACE = re.compile(r'^wl[a-zA-Z0-9_.-]{1,30}$')
TOKEN = re.compile(r'^[0-9a-f]{32}$')


def command(args, timeout=55, input=None):
    return subprocess.run(args, input=input, text=True, capture_output=True,
                          timeout=timeout, check=False)


def execute(data, *, run=command):
    if os.geteuid() != 0:
        raise PermissionError('Root required')
    if not isinstance(data, dict):
        raise ValueError('JSON object required')
    action = data.get('action')
    if action not in ('connect_saved', 'connect_new', 'confirm', 'hotspot'):
        raise ValueError('Unsupported action')
    if action == 'confirm':
        if set(data) != {'action', 'token'} or not isinstance(data['token'], str) or not TOKEN.fullmatch(data['token']):
            raise ValueError('Invalid confirmation')
        from universal_led.wifi_recovery_confirmation import confirm_recovery
        from universal_led.wifi_recovery_scheduler import STATE_DIR
        from universal_led.wifi_recovery import secure_open_state
        path = STATE_DIR / (data['token'] + '.json')
        try:
            with secure_open_state(path) as handle:
                pending = json.load(handle)
        except FileNotFoundError:
            return {'confirmed': False, 'reason': 'not_pending'}
        if pending.get('token') != data['token'] or pending.get('phase') is not None:
            return {'confirmed': False, 'reason': 'not_pending'}
        interface = pending.get('interface', '')
        previous = pending.get('previous_connection', '')
        if not IFACE.fullmatch(interface):
            raise ValueError('Invalid pending interface')
        active = run(['nmcli', '-g', 'GENERAL.CONNECTION', 'device', 'show', interface])
        if active.returncode != 0 or not active.stdout.strip() or active.stdout.strip() in (previous, '--'):
            return {'confirmed': False, 'reason': 'new_connection_not_verified'}
        return confirm_recovery(data['token'])
    if action == 'hotspot':
        if set(data) != {'action', 'enabled'} or type(data['enabled']) is not bool:
            raise ValueError('Invalid hotspot request')
        # Only toggle a pre-provisioned, fixed-name connection.
        result = run(['nmcli', 'connection', 'up' if data['enabled'] else 'down',
                      'id', 'Universal-LED-Setup'])
        return {'ok': result.returncode == 0}
    if action == 'connect_saved':
        allowed = {'action', 'interface', 'previous_connection', 'target_ssid', 'profile_uuid'}
    else:
        allowed = {'action', 'interface', 'previous_connection', 'target_ssid', 'password'}
    if set(data) != allowed:
        raise ValueError('Unexpected connection fields')
    from universal_led.wifi_recovery_scheduler import arm_recovery, validate_target
    interface = data['interface']
    previous = data['previous_connection']
    ssid = data['target_ssid']
    validate_target(interface, previous)
    if not isinstance(ssid, str) or not 1 <= len(ssid.encode('utf-8')) <= 32 or any(ord(c) < 32 for c in ssid):
        raise ValueError('Invalid SSID')
    if action == 'connect_saved':
        profile = data['profile_uuid']
        if not isinstance(profile, str) or not UUID.fullmatch(profile):
            raise ValueError('Invalid UUID')
        args = ['nmcli', '--wait', '45', 'connection', 'up', 'uuid', profile, 'ifname', interface]
        stdin = None
    else:
        password = data['password']
        if not isinstance(password, str) or (password and not 8 <= len(password) <= 63):
            raise ValueError('Invalid Wi-Fi password')
        # nmcli --ask consumes a secret through stdin rather than argv.
        # The web server passes it only over the local sudo helper stdin.
        args = ['nmcli', '--ask', '--wait', '45', 'device', 'wifi', 'connect', ssid, 'ifname', interface]
        stdin = password + '\n' if password else None
    # Never trust a browser-supplied rollback target. Confirm the actual active
    # Wi-Fi connection on this interface before scheduling any change.
    active = run(['nmcli', '-g', 'GENERAL.CONNECTION', 'device', 'show', interface])
    if active.returncode != 0 or active.stdout.strip() != previous:
        raise ValueError('Previous Wi-Fi connection does not match current state')
    token = arm_recovery(interface, previous)
    try:
        result = run(args, input=stdin)
        ok = result.returncode == 0
    except (OSError, subprocess.TimeoutExpired):
        ok = False
    return {'ok': ok, 'token': token, 'confirmation_required': True,
            'message': 'Connection requested' if ok else 'Connection failed; rollback remains armed'}


def main():
    try:
        if os.geteuid() != 0:
            raise PermissionError('Root required')
        raw = sys.stdin.buffer.read(4097)
        if len(raw) > 4096:
            raise ValueError('Request too large')
        data = json.loads(raw)
        print(json.dumps(execute(data)))
    except (ValueError, PermissionError, OSError, RuntimeError) as exc:
        print(json.dumps({'ok': False, 'error': str(exc)}))
        sys.exit(1)


if __name__ == '__main__':
    main()
