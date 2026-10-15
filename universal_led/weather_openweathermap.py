"""Optional OpenWeatherMap adapter with normalized weather snapshots."""
from urllib.parse import urlencode
from .weather_feed import WeatherSnapshot, _get_json


def fetch_openweathermap(location, unit='fahrenheit', api_key='', *, get_json=None):
    if not isinstance(location, str) or not location.strip():
        raise ValueError('Weather location is required')
    if unit not in ('fahrenheit', 'celsius'):
        raise ValueError('Invalid temperature unit')
    if not isinstance(api_key, str) or not api_key.strip():
        raise ValueError('OpenWeatherMap API key required')
    get_json = get_json or _get_json
    units = 'imperial' if unit == 'fahrenheit' else 'metric'
    args = urlencode({'q': location.strip(), 'appid': api_key.strip(), 'units': units})
    # The current weather endpoint provides current temperature and min/max
    # reported for the current period, not a full-day forecast.
    data = get_json('https://api.openweathermap.org/data/2.5/weather?' + args)
    main = data['main']
    conditions = data.get('weather') or []
    code = int(conditions[0].get('id', 800)) if conditions else 800
    if 200 <= code < 300:
        wmo = 95
    elif 300 <= code < 600:
        wmo = 61
    elif 600 <= code < 700:
        wmo = 71
    elif 700 <= code < 800:
        wmo = 45
    elif code == 800:
        wmo = 0
    elif code == 801:
        wmo = 1
    elif code == 802:
        wmo = 2
    else:
        wmo = 3
    return WeatherSnapshot(
        location=str(data.get('name') or location.strip()),
        temperature=float(main['temp']),
        high=float(main.get('temp_max', main['temp'])),
        low=float(main.get('temp_min', main['temp'])),
        weather_code=wmo,
        observed_at=str(data.get('dt', '')))
