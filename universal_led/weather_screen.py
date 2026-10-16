"""Compact 64x32 icon-led weather display, independent of the provider."""
from dataclasses import dataclass

from .display import Framebuffer
from .mlb_classic import small
from .weather_feed import WeatherSnapshot, weather_description
from .weather_icons import draw_weather_icon
from .safe_layout import MARGIN, fit_small


@dataclass(frozen=True)
class WeatherScreen:
    weather: WeatherSnapshot
    unit: str = 'fahrenheit'

    def render(self):
        frame = Framebuffer(64, 32)
        gold = (239, 195, 95)
        white = (235, 235, 225)
        blue = (112, 182, 240)
        location = fit_small(self.weather.location.upper().replace(',', ''), 60)
        small(frame, location, MARGIN, MARGIN, gold)
        draw_weather_icon(frame, 2, 8, self.weather.weather_code,
                          is_day=self.weather.is_day)
        suffix = 'F' if self.unit == 'fahrenheit' else 'C'
        temperature = f'{round(self.weather.temperature)}{suffix}'
        small(frame, fit_small(temperature, 38), 24, 10, white)
        condition = weather_description(self.weather.weather_code)
        # The narrow right column favors concise condition labels.
        label = {'PARTLY CLOUDY':'PARTLY','DRIZZLE':'RAIN'}.get(condition,condition)
        small(frame, fit_small(label, 38), 24, 18, blue)
        high_low = f'H{round(self.weather.high)} L{round(self.weather.low)}'
        small(frame, fit_small(high_low, 60), MARGIN, 25, gold)
        return frame
