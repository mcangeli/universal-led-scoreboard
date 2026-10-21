"""Persistent, validated plugin preferences outside executable plugin packages."""
from __future__ import annotations
import json
import os
import tempfile
from pathlib import Path
from .plugin_manifest import ManifestError
from .plugin_settings_schema import load_settings_schema, validated_settings


def read_plugin_settings(package, data_root, plugin_id):
    fields = load_settings_schema(package)
    path = Path(data_root) / (plugin_id + ".json")
    if not path.exists():
        return validated_settings(fields, {})
    if path.is_symlink() or not path.is_file() or path.stat().st_size > 16384:
        raise ManifestError("unsafe plugin settings file")
    return validated_settings(fields, json.loads(path.read_text(encoding="utf-8")))


def save_plugin_settings(package, data_root, plugin_id, values):
    fields = load_settings_schema(package)
    validated = validated_settings(fields, values)
    directory = Path(data_root)
    if directory.is_symlink():
        raise ManifestError("unsafe plugin settings directory")
    directory.mkdir(parents=True, exist_ok=True)
    destination = directory / (plugin_id + ".json")
    if destination.is_symlink():
        raise ManifestError("unsafe plugin settings destination")
    fd, temporary = tempfile.mkstemp(prefix=".uls-plugin-settings-", dir=directory)
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as handle:
            json.dump(validated, handle, sort_keys=True, indent=2)
            handle.write("\n")
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(temporary, destination)
    finally:
        if os.path.exists(temporary):
            os.unlink(temporary)
    return validated
