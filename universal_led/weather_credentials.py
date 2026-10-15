"""Store weather provider credentials separately from public settings."""
import json
import os
from pathlib import Path
import tempfile


def _path(directory):
    return Path(directory) / 'weather_credentials.json'


def has_openweathermap_key(directory):
    return bool(load_openweathermap_key(directory))


def load_openweathermap_key(directory):
    path = _path(directory)
    if not path.exists():
        return ''
    value = json.loads(path.read_text(encoding='utf-8'))
    return value.get('openweathermap_api_key', '') if isinstance(value, dict) else ''


def save_openweathermap_key(directory, key):
    if not isinstance(key, str) or not 1 <= len(key.strip()) <= 256:
        raise ValueError('Invalid OpenWeatherMap API key')
    root = Path(directory)
    root.mkdir(parents=True, exist_ok=True)
    fd, name = tempfile.mkstemp(prefix='.weather-secret-', dir=root)
    try:
        os.fchmod(fd, 0o600)
        with os.fdopen(fd, 'w', encoding='utf-8') as stream:
            json.dump({'openweathermap_api_key': key.strip()}, stream)
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(name, _path(directory))
    finally:
        if os.path.exists(name):
            os.unlink(name)
