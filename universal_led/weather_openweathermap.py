"""Optional OpenWeatherMap adapter with normalized weather snapshots."""
from urllib.parse import urlencode
import re
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
    query = location.strip()
    zip_match = re.fullmatch(r'(\\d{5})(?:-\\d{4})?(?:,\\s*US)?', query, re.IGNORECASE)
    display_location = None
    if zip_match:
        zip_args = urlencode({'zip': zip_match.group(1) + ',US', 'appid': api_key.strip()})
        place = get_json('https://api.openweathermap.org/geo/1.0/zip?' + zip_args)
        display_location = str(place.get('name') or '').strip() or None
        args = urlencode({'lat': place['lat'], 'lon': place['lon'], 'appid': api_key.strip(), 'units': units})
    else:
        args = urlencode({'q': query, 'appid': api_key.strip(), 'units': units})
    # The current weather endpoint provides current temperature and min/max
    # reported for the current period, not a full-day forecast.
    data = get_json('https://api.openweathermap.org/data/2.5/weather?' + args)
    if zip_match:
        # Reverse geocoding supplies the state, which the ZIP endpoint omits.
        try:
            reverse_args = urlencode({'lat': place['lat'], 'lon': place['lon'], 'limit': 1, 'appid': api_key.strip()})
            matches = get_json('https://api.openweathermap.org/geo/1.0/reverse?' + reverse_args)
            if matches and isinstance(matches[0], dict):
                match = matches[0]
                city = str(match.get('name') or display_location or '').strip()
                state = str(match.get('state') or '').strip()
                display_location = ', '.join(part for part in (city, state) if part)
        except (OSError, ValueError, KeyError, TypeError, IndexError):
            pass
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
        location=display_location or str(data.get('name') or location.strip()),
        temperature=float(main['temp']),
        high=float(main.get('temp_max', main['temp'])),
        low=float(main.get('temp_min', main['temp'])),
        weather_code=wmo,
        observed_at=str(data.get('dt', '')))
