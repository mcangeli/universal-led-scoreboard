"""Weather polling runs separately from the matrix rendering thread."""
import threading

from .time_weather_settings import load_time_weather
from .weather_feed import BackgroundWeather, fetch_weather
from .weather_openweathermap import fetch_openweathermap
from .weather_credentials import load_openweathermap_key


class WeatherWorker:
    def __init__(self, directory, *, cache=None, wait_seconds=30):
        self.directory = directory
        self.cache = cache if cache is not None else BackgroundWeather(fetch=self._fetch)
        self._provider = 'open-meteo'
        self.wait_seconds = wait_seconds
        self._stop = threading.Event()
        self._thread = None

    def _fetch(self, location, unit):
        if self._provider == 'openweathermap':
            return fetch_openweathermap(location,unit,load_openweathermap_key(self.directory))
        return fetch_weather(location,unit)

    def refresh(self):
        settings = load_time_weather(self.directory)
        if settings['weather_enabled'] and settings['location'].strip():
            provider=settings['weather_provider']
            if provider != self._provider:
                self._provider=provider
                # Reset cache when provider changes; do not show data from the old provider.
                if isinstance(self.cache,BackgroundWeather):
                    self.cache.invalidate()
            self.cache.update(settings['location'], settings['temperature_unit'])

    def start(self):
        if self._thread is not None and self._thread.is_alive():
            return
        self._stop.clear()
        def worker():
            while not self._stop.is_set():
                try:
                    self.refresh()
                except (OSError, ValueError, TypeError):
                    pass
                self._stop.wait(self.wait_seconds)
        self._thread = threading.Thread(target=worker, daemon=True, name='scoreboard-weather')
        self._thread.start()

    def snapshot(self):
        return self.cache.snapshot()

    def stop(self):
        self._stop.set()
        if self._thread is not None:
            self._thread.join(timeout=2)
