#!/usr/bin/env python3
"""Interactive, root-only hotspot provisioning; never places PSK in argv."""
import getpass
import os
import secrets
import subprocess
import sys

NAME = 'Universal-LED-Setup'
WORDS = ('river', 'maple', 'cedar', 'silver', 'amber', 'brave', 'falcon', 'meadow',
         'copper', 'sunset', 'willow', 'harbor', 'forest', 'stone', 'orbit', 'lucky')

def generated_password():
    return '-'.join(secrets.choice(WORDS) for _ in range(3)) + str(secrets.randbelow(90) + 10)

def valid_password(value):
    return isinstance(value, str) and value.isascii() and value.isprintable() and 8 <= len(value.encode()) <= 63 and not any(c in value for c in ('"', "'", '\\'))

def provision(password, *, run=subprocess.run):
    if not valid_password(password):
        raise ValueError('Use 8-63 printable ASCII characters without quotes or backslashes')
    def call(args, **kwargs):
        return run(['nmcli', *args], capture_output=True, text=True, timeout=25,
                   check=False, **kwargs)
    existing = call(['-g', '802-11-wireless.mode', 'connection', 'show', NAME])
    if existing.returncode == 0:
        if existing.stdout.strip() != 'ap':
            raise ValueError('Existing profile name is not a hotspot; refusing to overwrite')
        return False
    added = call(['connection', 'add', 'type', 'wifi', 'con-name', NAME,
                  'ssid', NAME, '802-11-wireless.mode', 'ap',
                  '802-11-wireless.band', 'bg', 'ipv4.method', 'shared',
                  'connection.autoconnect', 'no', 'wifi-sec.key-mgmt', 'wpa-psk'])
    if added.returncode:
        raise RuntimeError('Could not create hotspot profile')
    # Password flows only through stdin; do not print subprocess output.
    script = 'set wifi-sec.psk "' + password + '"\nsave persistent\nquit\n'
    saved = call(['connection', 'edit', NAME], input=script)
    if saved.returncode:
        call(['connection', 'delete', 'id', NAME])
        raise RuntimeError('Could not store hotspot password; profile removed')
    return True

def main():
    if os.geteuid() != 0:
        sys.exit('Run with sudo')
    proposed = generated_password()
    print('Suggested hotspot password: ' + proposed)
    custom = getpass.getpass('Custom password (Enter to use suggested): ')
    password = custom or proposed
    try:
        created = provision(password)
    except (ValueError, RuntimeError, OSError, subprocess.TimeoutExpired) as exc:
        sys.exit(str(exc))
    if created:
        print('Hotspot: ' + NAME)
        print('Password: ' + password)
        print('Store this password securely; it will not be shown in the web UI.')
    else:
        print('Existing Universal-LED-Setup hotspot retained. Password unchanged.')

if __name__ == '__main__':
    main()
