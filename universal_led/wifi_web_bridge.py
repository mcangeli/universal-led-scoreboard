"""Unprivileged web-to-root Wi-Fi bridge. No shell or password logging."""
import json
import subprocess

HELPER = '/usr/local/libexec/universal-led-wifi-control'


def request_wifi_change(payload, *, run=subprocess.run):
    if not isinstance(payload, dict):
        raise ValueError('JSON object required')
    raw = json.dumps(payload, ensure_ascii=False)
    if len(raw.encode('utf-8')) > 4096:
        raise ValueError('Request too large')
    try:
        result = run(['sudo', '-n', HELPER], input=raw, text=True,
                     capture_output=True, timeout=75, check=False)
        response = json.loads(result.stdout)
        if not isinstance(response, dict):
            raise ValueError('Invalid helper response')
        return response if result.returncode == 0 else {
            'ok': False, 'error': response.get('error', 'Wi-Fi helper failed')}
    except (OSError, subprocess.TimeoutExpired, ValueError):
        return {'ok': False, 'error': 'Wi-Fi helper unavailable or invalid response'}
