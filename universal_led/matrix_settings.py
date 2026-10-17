"""Validated physical matrix settings; defaults match the deployed Pi 3 service.

This module intentionally does not manage systemd or write privileged paths.
"""
from __future__ import annotations

import json
from pathlib import Path

DEFAULTS = {
    "enabled": True,
    "mapping": "adafruit-hat",
    "brightness": 40,
    "gpio_slowdown": 4,
    "interval": 0.2,
}
ALLOWED_MAPPINGS = ("regular", "adafruit-hat", "adafruit-hat-pwm", "compute-module")


def validate_matrix_settings(value):
    if not isinstance(value, dict):
        raise ValueError("Matrix settings must be an object")
    unknown = set(value) - set(DEFAULTS)
    if unknown:
        raise ValueError("Unknown matrix settings: " + ", ".join(sorted(unknown)))
    result = dict(DEFAULTS)
    result.update(value)
    if type(result["enabled"]) is not bool:
        raise ValueError("enabled must be a boolean")
    if result["mapping"] not in ALLOWED_MAPPINGS:
        raise ValueError("Unsupported hardware mapping")
    for name, minimum, maximum in (("brightness", 1, 100), ("gpio_slowdown", 0, 10)):
        number = result[name]
        if type(number) is not int or not minimum <= number <= maximum:
            raise ValueError(f"{name} must be an integer from {minimum} to {maximum}")
    interval = result["interval"]
    if type(interval) not in (int, float) or not 0.05 <= interval <= 10:
        raise ValueError("interval must be between 0.05 and 10 seconds")
    return result


def load_matrix_settings(path):
    path = Path(path)
    if not path.exists():
        return dict(DEFAULTS)
    return validate_matrix_settings(json.loads(path.read_text(encoding="utf-8")))
