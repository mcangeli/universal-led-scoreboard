"""Compact 64x32 weather display, independent of the provider."""
from dataclasses import dataclass

from .display import Framebuffer
from .mlb_classic import small
from .weather_feed import WeatherSnapshot, weather_description


@dataclass(frozen=True)
class WeatherScreen:
    weather: WeatherSnapshot
    unit: str = 'fahrenheit'

    def render(self):
        frame = Framebuffer(64, 32)
        gold = (239, 195, 95)
        white = (235, 235, 225)
        blue = (112, 182, 240)
        small(frame, self.weather.location.upper()[:16], 0, 0, gold)
        condition = weather_description(self.weather.weather_code)
        small(frame, condition[:16], 0, 9, blue)
        suffix = 'F' if self.unit == 'fahrenheit' else 'C'
        temperature = f'{round(self.weather.temperature)}{suffix}'
        small(frame, temperature, 0, 19, white)
        high_low = f'H{round(self.weather.high)} L{round(self.weather.low)}'
        small(frame, high_low[:16], 0, 27, gold)
        return frame
