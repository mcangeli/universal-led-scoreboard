"""Construct Bullpen plugin instances from a trusted, explicitly supplied factory.

This module never discovers, imports, or installs third-party packages.
The caller is responsible for separately authorizing and isolating code.
"""
from __future__ import annotations

from typing import Callable

from .bullpen_config import BullpenColors, BullpenLayout, BullpenMLBConfig
from .bullpen_screen import BullpenScreen


class BullpenFactoryError(ValueError):
    """The plugin factory does not implement the Bullpen class contract."""


def construct_bullpen_screen(
    factory: Callable,
    *,
    plugin_settings: dict | None = None,
    fonts: dict | None = None,
    coordinates: dict | None = None,
    colors: dict | None = None,
) -> BullpenScreen:
    """Create the standard Config, Data, Renderer trio and return its ULS screen.

    Only call with a previously trusted factory. This function is not a
    sandbox, and should not be used on unreviewed repository code.
    """
    if not callable(factory):
        raise BullpenFactoryError("Bullpen factory must be callable")
    classes = factory()
    if not isinstance(classes, tuple) or len(classes) != 3:
        raise BullpenFactoryError("Bullpen factory must return (Config, Data, Renderer)")
    config_type, data_type, renderer_type = classes
    if not all(callable(item) for item in classes):
        raise BullpenFactoryError("Bullpen factory returned non-callable classes")
    base = BullpenMLBConfig(plugin_settings)
    config = config_type(base)
    data = data_type(config)
    renderer = renderer_type(config, BullpenLayout(fonts, coordinates), BullpenColors(colors))
    for name in ("update",):
        if not callable(getattr(data, name, None)):
            raise BullpenFactoryError("Bullpen Data missing " + name)
    for name in ("render", "can_render", "wait_time", "reset"):
        if not callable(getattr(renderer, name, None)):
            raise BullpenFactoryError("Bullpen Renderer missing " + name)
    return BullpenScreen(data, renderer)
