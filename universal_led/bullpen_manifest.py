"""Read Bullpen pyproject.toml metadata without importing third-party code."""
from __future__ import annotations

import re
import tomllib
from pathlib import Path

from .plugin_manifest import ManifestError

ENTRY_GROUP = "bullpen.mlbled.plugin"
ENTRY_PATTERN = re.compile(r"^[A-Za-z_]\w*(?:\.[A-Za-z_]\w*)*:[A-Za-z_]\w*$")
ID_PATTERN = re.compile(r"^[a-z][a-z0-9]*(?:[._-][a-z0-9]+)*$")


def inspect_bullpen_metadata(package: Path) -> dict:
    manifest_file = package / "pyproject.toml"
    if manifest_file.is_symlink() or not manifest_file.is_file():
        raise ManifestError("Bullpen plugin requires pyproject.toml")
    if manifest_file.stat().st_size > 65536:
        raise ManifestError("Bullpen pyproject.toml exceeds 64 KiB")
    try:
        raw = tomllib.loads(manifest_file.read_text(encoding="utf-8"))
        project = raw["project"]
        entries = project["entry-points"][ENTRY_GROUP]
    except (OSError, UnicodeError, ValueError, KeyError, TypeError) as exc:
        raise ManifestError("invalid Bullpen pyproject.toml") from exc
    if not isinstance(entries, dict) or len(entries) != 1:
        raise ManifestError("Bullpen adapter currently supports exactly one entry point")
    plugin_id, entry = next(iter(entries.items()))
    if not isinstance(plugin_id, str) or not ID_PATTERN.fullmatch(plugin_id) or len(plugin_id) > 100:
        raise ManifestError("invalid Bullpen plugin id")
    if not isinstance(entry, str) or not ENTRY_PATTERN.fullmatch(entry):
        raise ManifestError("invalid Bullpen entry point")
    name, version = project.get("name"), project.get("version")
    if not isinstance(name, str) or not name.strip() or len(name) > 120:
        raise ManifestError("invalid Bullpen project name")
    if not isinstance(version, str) or not re.fullmatch(r"[0-9]+\.[0-9]+\.[0-9]+(?:[-+][a-zA-Z0-9.-]+)?", version):
        raise ManifestError("invalid Bullpen project version")
    description = project.get("description", "")
    if not isinstance(description, str) or len(description) > 1000:
        raise ManifestError("invalid Bullpen description")
    return {"id": plugin_id, "name": name, "version": version,
            "description": description, "capabilities": ["screen"],
            "format": "bullpen", "entry_point": entry,
            "installable": False,
            "compatibility": "Bullpen runtime adapter not installed; review only"}
