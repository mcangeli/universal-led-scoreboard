"""Minimal Bullpen MLBConfig and Layout adapters for ULS.

These adapters provide the configuration contract without importing Bullpen or
third-party plugin code. Unsupported font formats require later integration.
"""
from __future__ import annotations

from datetime import date, datetime
from types import MappingProxyType
from typing import Any, Mapping


class BullpenMLBConfig:
    def __init__(self, plugin_config: Mapping[str, Any] | None = None,
                 *, scrolling_speed: float = 1.0, time_format: str = "12h"):
        if not isinstance(scrolling_speed, (int, float)) or scrolling_speed <= 0:
            raise ValueError("scrolling_speed must be positive")
        if time_format not in ("12h", "24h"):
            raise ValueError("time_format must be 12h or 24h")
        if plugin_config is not None and not isinstance(plugin_config, Mapping):
            raise ValueError("plugin_config must be a mapping")
        self._plugin_config = dict(plugin_config or {})
        self.scrolling_speed = float(scrolling_speed)
        self.time_format = time_format

    @property
    def plugin_config(self) -> dict[str, Any]:
        return dict(self._plugin_config)

    def parse_today(self) -> date:
        return date.today()

    def is_postseason(self) -> bool:
        # ULS must supply authoritative season state before enabling plugins
        # whose logic depends on postseason detection.
        raise NotImplementedError("postseason state requires MLB season provider")


class BullpenLayout:
    def __init__(self, fonts: Mapping[str, Any] | None = None,
                 coordinates: Mapping[str, Any] | None = None):
        self.width = 64
        self.height = 32
        self._fonts = dict(fonts or {})
        self._coordinates = dict(coordinates or {})

    def font(self, keypath: str) -> dict[str, Any]:
        if keypath not in self._fonts:
            raise KeyError("Bullpen font not configured: " + keypath)
        return {"font": self._fonts[keypath]}

    def coords(self, keypath: str) -> Any:
        return self._coordinates[keypath]


class BullpenColors:
    def __init__(self, values: Mapping[str, Any] | None = None):
        self._values = dict(values or {})

    def color(self, keypath: str) -> dict[str, int]:
        value = self._values[keypath]
        if isinstance(value, tuple) and len(value) == 3:
            value = dict(red=value[0], green=value[1], blue=value[2])
        if not isinstance(value, dict) or any(k not in value for k in ("red", "green", "blue")):
            raise ValueError("expected RGB color")
        return {key: value[key] for key in ("red", "green", "blue")}

    def graphics_color(self, keypath: str) -> tuple[int, int, int]:
        value = self.color(keypath)
        return (value["red"], value["green"], value["blue"])
