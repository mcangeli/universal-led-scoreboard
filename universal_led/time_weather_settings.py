"""Sport-independent clock and weather display preferences."""
import json
from pathlib import Path
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError

from .config_store import save_config

DEFAULT_TIME_WEATHER = {
    'version': 1,
    'clock_enabled': True,
    'weather_enabled': False,
    'timezone': 'America/New_York',
    'time_format': '12h',
    'temperature_unit': 'fahrenheit',
    'location': '',
    'rotation_interval': 5,
}


def validate_time_weather(value):
    if not isinstance(value, dict) or set(value) != set(DEFAULT_TIME_WEATHER):
        raise ValueError('Invalid time/weather settings')
    if type(value['version']) is not int or value['version'] != 1:
        raise ValueError('Unsupported time/weather version')
    for key in ('clock_enabled', 'weather_enabled'):
        if type(value[key]) is not bool:
            raise ValueError('Invalid toggle: ' + key)
    if not isinstance(value['timezone'], str) or len(value['timezone']) > 100:
        raise ValueError('Invalid timezone')
    try:
        ZoneInfo(value['timezone'])
    except (ZoneInfoNotFoundError, ValueError, KeyError) as exc:
        raise ValueError('Unknown timezone') from exc
    if value['time_format'] not in ('12h', '24h'):
        raise ValueError('Invalid clock format')
    if value['temperature_unit'] not in ('fahrenheit', 'celsius'):
        raise ValueError('Invalid temperature unit')
    if not isinstance(value['location'], str) or len(value['location']) > 120:
        raise ValueError('Invalid location')
    if type(value['rotation_interval']) is not int or not 1 <= value['rotation_interval'] <= 20:
        raise ValueError('Invalid rotation interval')
    return json.loads(json.dumps(value))


def load_time_weather(directory):
    path = Path(directory) / 'time_weather.json'
    if not path.exists():
        return dict(DEFAULT_TIME_WEATHER)
    return validate_time_weather(json.loads(path.read_text(encoding='utf-8')))


def save_time_weather(directory, value):
    settings = validate_time_weather(value)
    save_config(directory, 'time_weather', settings)
    return settings
