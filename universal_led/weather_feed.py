"""Open-Meteo weather lookup and network-independent cached snapshots."""
from dataclasses import dataclass
from datetime import datetime, timezone
import json
import threading
import time
from urllib.parse import urlencode
from urllib.request import Request, urlopen


@dataclass(frozen=True)
class WeatherSnapshot:
    location: str
    temperature: float
    high: float
    low: float
    weather_code: int
    observed_at: str


def weather_description(code):
    if code == 0:
        return 'CLEAR'
    if code in (1, 2):
        return 'PARTLY CLOUDY'
    if code == 3:
        return 'CLOUDY'
    if code in (45, 48):
        return 'FOG'
    if code in (51, 53, 55, 56, 57):
        return 'DRIZZLE'
    if code in (61, 63, 65, 66, 67, 80, 81, 82):
        return 'RAIN'
    if code in (71, 73, 75, 77, 85, 86):
        return 'SNOW'
    if code in (95, 96, 99):
        return 'STORMS'
    return 'WEATHER'


def _get_json(url):
    request = Request(url, headers={'User-Agent': 'UniversalLEDScoreboard/0.1'})
    with urlopen(request, timeout=8) as response:
        payload = response.read(1000001)
    if len(payload) > 1000000:
        raise ValueError('Weather response too large')
    return json.loads(payload)


def fetch_weather(location, unit='fahrenheit', *, get_json=None):
    """Resolve city/ZIP through geocoding; retrieve current and daily forecast."""
    if not isinstance(location, str) or not location.strip():
        raise ValueError('Weather location is required')
    if unit not in ('fahrenheit', 'celsius'):
        raise ValueError('Invalid temperature unit')
    get_json = get_json or _get_json
    geo = get_json('https://geocoding-api.open-meteo.com/v1/search?' +
                   urlencode({'name': location.strip(), 'count': 1, 'language': 'en', 'format': 'json'}))
    places = geo.get('results') or []
    if not places:
        raise ValueError('Weather location not found')
    place = places[0]
    args = {'latitude': place['latitude'], 'longitude': place['longitude'],
            'current': 'temperature_2m,weather_code',
            'daily': 'temperature_2m_max,temperature_2m_min',
            'temperature_unit': unit, 'timezone': 'auto', 'forecast_days': 1}
    data = get_json('https://api.open-meteo.com/v1/forecast?' + urlencode(args))
    current = data['current']
    daily = data['daily']
    return WeatherSnapshot(
        location=place['name'], temperature=float(current['temperature_2m']),
        high=float(daily['temperature_2m_max'][0]),
        low=float(daily['temperature_2m_min'][0]),
        weather_code=int(current['weather_code']),
        observed_at=str(current.get('time') or datetime.now(timezone.utc).isoformat()))


class BackgroundWeather:
    """Refresh outside the render path; retain last good result on failure."""

    def __init__(self, *, fetch=None, clock=None, refresh_seconds=900):
        self.fetch = fetch or fetch_weather
        self.clock = clock or time.monotonic
        self.refresh_seconds = refresh_seconds
        self._lock = threading.Lock()
        self._snapshot = None
        self._key = None
        self._next = 0.0
        self.error = None

    def invalidate(self):
        with self._lock:
            self._key = None
            self._snapshot = None
            self._next = 0.0
            self.error = None

    def update(self, location, unit='fahrenheit', *, identity=None):
        key = (location.strip(), unit, identity)
        now = self.clock()
        with self._lock:
            if key != self._key:
                self._key = key
                self._next = 0
                self._snapshot = None
            if now < self._next:
                return self._snapshot
            self._next = now + self.refresh_seconds
        try:
            snapshot = self.fetch(location.strip(), unit)
        except (OSError, ValueError, KeyError, TypeError, IndexError) as exc:
            with self._lock:
                self.error = str(exc)
                return self._snapshot
        with self._lock:
            self._snapshot = snapshot
            self.error = None
            return snapshot

    def snapshot(self):
        with self._lock:
            return self._snapshot
