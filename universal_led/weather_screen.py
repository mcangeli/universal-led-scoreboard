"""Compact 64x32 icon-led weather display, independent of the provider."""
from dataclasses import dataclass

from .display import Framebuffer
from .mlb_classic import small
from .weather_feed import WeatherSnapshot, weather_description
from .weather_icons import draw_weather_icon


@dataclass(frozen=True)
class WeatherScreen:
    weather: WeatherSnapshot
    unit: str = 'fahrenheit'

    def render(self):
        frame = Framebuffer(64, 32)
        gold = (239, 195, 95)
        white = (235, 235, 225)
        blue = (112, 182, 240)
        location = self.weather.location.upper()[:15]
        small(frame, location, 0, 0, gold)
        draw_weather_icon(frame, 1, 9, self.weather.weather_code)
        suffix = 'F' if self.unit == 'fahrenheit' else 'C'
        temperature = f'{round(self.weather.temperature)}{suffix}'
        small(frame, temperature[:10], 23, 10, white)
        condition = weather_description(self.weather.weather_code)
        # The narrow right column favors concise condition labels.
        label = {'PARTLY CLOUDY':'PARTLY','DRIZZLE':'RAIN'}.get(condition,condition)
        small(frame, label[:10], 23, 18, blue)
        high_low = f'H{round(self.weather.high)} L{round(self.weather.low)}'
        small(frame, high_low[:16], 0, 27, gold)
        return frame
