"""Conservative NetworkManager hotspot fallback and saved-Wi-Fi recovery.

Designed for a root systemd timer. Never runs while a Wi-Fi rollback is armed.
Never touches Ethernet or the existing MLB setup hotspot.
"""
from __future__ import annotations
import subprocess
from pathlib import Path

AP = 'Universal-LED-Setup'
PENDING = Path('/run/universal-led-scoreboard/wifi-recovery')

def maintain(*, run=subprocess.run, pending=PENDING):
    if pending.exists() and any(pending.glob('*.json')):
        return 'rollback_pending'
    def nm(*args):
        try:
            return run(['nmcli', *args], capture_output=True, text=True,
                       timeout=35, check=False)
        except (OSError, subprocess.TimeoutExpired):
            return None
    devices = nm('-t', '-f', 'DEVICE,TYPE,STATE,CONNECTION', 'device', 'status')
    if devices is None or devices.returncode:
        return 'networkmanager_unavailable'
    from .wifi_diagnostics import _split_nmcli
    wifi = [p for line in devices.stdout.splitlines()
            if len(p := _split_nmcli(line)) >= 4 and p[1] == 'wifi']
    if not wifi:
        return 'no_wifi_interface'
    device = wifi[0][0]
    active = ':'.join(wifi[0][3:])
    if wifi[0][2] == 'connected':
        # Never interrupt an active management hotspot or client session.
        return 'hotspot_active' if active == AP else 'client_connected'
    profile = nm('-g', '802-11-wireless.mode', 'connection', 'show', AP)
    if profile is None or profile.returncode or profile.stdout.strip() != 'ap':
        return 'hotspot_not_provisioned'
    saved = nm('-t', '-f', 'NAME,UUID,TYPE,DEVICE', 'connection', 'show')
    if saved is None or saved.returncode:
        return 'profiles_unavailable'
    # Try known client profiles, never the AP; no secrets in process arguments.
    for line in saved.stdout.splitlines():
        parts = _split_nmcli(line)
        if len(parts) != 4 or parts[2] not in ('wifi', '802-11-wireless') or parts[0] == AP:
            continue
        mode = nm('-g', '802-11-wireless.mode', 'connection', 'show', 'uuid', parts[1])
        if mode is None or mode.returncode or mode.stdout.strip() == 'ap':
            continue
        # NetworkManager may temporarily stop the AP while trying a client.
        result = nm('--wait', '15', 'connection', 'up', 'uuid', parts[1], 'ifname', device)
        if result is not None and result.returncode == 0:
            return 'client_restored'
    # An attempted client connection may have torn down the hotspot.
    # Reassert it even if the initial snapshot showed AP active.
    result = nm('--wait', '15', 'connection', 'up', 'id', AP, 'ifname', device)
    return 'hotspot_started' if result is not None and result.returncode == 0 else 'hotspot_failed'

def main():
    import os
    if os.geteuid() != 0:
        raise PermissionError('Root required')
    print(maintain())

if __name__ == '__main__':
    main()
