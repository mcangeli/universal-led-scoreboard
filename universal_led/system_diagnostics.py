"""Read-only, bounded Raspberry Pi diagnostics for the LAN configurator."""
from __future__ import annotations
import os
import platform
import shutil
import subprocess
from pathlib import Path

SERVICE = 'universal-led-scoreboard.service'

def service_status():
    """Prefer the supported system unit, retaining legacy user-unit support."""
    candidates = (
        (['systemctl', 'show', 'uls-web.service'], 'uls-web.service'),
        (['systemctl', '--user', 'show', SERVICE], SERVICE),
    )
    for command, unit in candidates:
        try:
            result = subprocess.run(
                command + ['--property=LoadState,ActiveState,SubState,UnitFileState',
                           '--no-pager'],
                capture_output=True, text=True, timeout=2, check=False)
        except (OSError, subprocess.TimeoutExpired):
            continue
        if result.returncode:
            continue
        values = dict(line.split('=', 1) for line in result.stdout.splitlines() if '=' in line)
        if values.get('LoadState') != 'loaded':
            continue
        return {'state':values.get('ActiveState') or 'unknown',
                'substate':values.get('SubState') or 'unknown',
                'enabled':values.get('UnitFileState') or 'unknown',
                'loaded':values.get('LoadState') or 'unknown',
                'unit':unit}
    return {'state':'unavailable','detail':'No installed scoreboard web service found'}


def system_status():
    disk = shutil.disk_usage(Path.home())
    model_path = Path('/proc/device-tree/model')
    try:
        model = model_path.read_bytes().replace(b'\x00', b'').decode('utf-8', errors='replace').strip()
    except OSError:
        model = platform.machine()
    try:
        temp = int(Path('/sys/class/thermal/thermal_zone0/temp').read_text().strip()) / 1000
    except (OSError, ValueError):
        temp = None
    try:
        uptime = int(float(Path('/proc/uptime').read_text().split()[0]))
    except (OSError, ValueError, IndexError):
        uptime = None
    return {'model':model, 'os':platform.system()+' '+platform.release(),
            'python':platform.python_version(), 'hostname':platform.node(),
            'temperature_c':temp, 'host_uptime_seconds':uptime,
            'disk_free_gb':round(disk.free / 1073741824, 2),
            'service':service_status(), 'led_hardware':'not configured',
            'backend':'browser emulator'}
