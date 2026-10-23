"""Subprocess-only execution of enabled native screen plugins.

A timeout bounds rendering; never import plugin code into the web process.
This is process isolation, not a security sandbox for hostile Python.
"""
from __future__ import annotations
import json
import subprocess
import sys
from pathlib import Path
from .display import Framebuffer
from .plugin_manifest import load_plugin_manifest
from .plugin_registry import read_registry

MAX_FRAME = 64 * 32 * 3


def enabled_screen_ids(root, registry):
    records = read_registry(registry)
    result = []
    for plugin_id, record in sorted(records.items()):
        package = Path(root) / plugin_id
        if not record["enabled"] or package.is_symlink() or not package.is_dir():
            continue
        try:
            manifest = load_plugin_manifest(package)
            if manifest.plugin_id == plugin_id and "screen" in manifest.capabilities:
                result.append(plugin_id)
        except (OSError, ValueError):
            continue
    return tuple(result)


class NativePluginSlot:
    def __init__(self, plugin_id, root="/var/lib/uls/plugins", timeout=1.5):
        self.plugin_id = plugin_id
        self.root = Path(root)
        self.timeout = timeout
        self.display_seconds = 12
        self.appearance_every_pages = 10 if plugin_id == 'daily-calendar' else 1
        from .plugin_settings_store import read_plugin_settings
        try:
            settings = read_plugin_settings(self.root / self.plugin_id,
                                            self.root.parent / 'plugin-settings', self.plugin_id)
            self.display_seconds = settings['display_seconds']
            self.appearance_every_pages = settings['appearance_every_pages']
        except (OSError, ValueError, KeyError):
            pass

    def frame(self, *, live_games=False, selected=True, now=None):
        if live_games or not selected:
            return None
        from .plugin_settings_store import read_plugin_settings
        try:
            settings = read_plugin_settings(self.root / self.plugin_id,
                                            self.root.parent / 'plugin-settings', self.plugin_id)
        except (OSError, ValueError):
            settings = {}
        self.display_seconds = settings.get('display_seconds', 12)
        self.appearance_every_pages = settings.get('appearance_every_pages', self.appearance_every_pages)
        completed = subprocess.run(
            [sys.executable, "-m", "universal_led.native_plugin_worker",
             str(self.root), self.plugin_id, json.dumps(settings)],
            stdout=subprocess.PIPE, stderr=subprocess.PIPE,
            timeout=self.timeout, check=True)
        raw = completed.stdout
        if len(raw) != MAX_FRAME:
            raise ValueError("plugin must return exactly 64x32 RGB pixels")
        frame = Framebuffer(64, 32)
        for y in range(32):
            offset = y * 64 * 3
            frame.pixels[y] = [tuple(raw[offset + x*3:offset + x*3 + 3]) for x in range(64)]
        return frame


def enabled_screen_slots(root, registry):
    return tuple(NativePluginSlot(plugin_id, root) for plugin_id in enabled_screen_ids(root, registry))
