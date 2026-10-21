"""ULS plugin manifest validation and read-only discovery.

Discovery never imports or executes third-party plugin code. Execution and
installation will be separate, explicitly authorized lifecycle operations.
"""
from __future__ import annotations

import json
import tomllib
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Mapping

PLUGIN_API_VERSION = 1
_ID = re.compile(r"^[a-z][a-z0-9]*(?:[._-][a-z0-9]+)*$")
_VERSION = re.compile(r"^[0-9]+\.[0-9]+\.[0-9]+(?:[-+][a-zA-Z0-9.-]+)?$")
_CAPABILITIES = frozenset({"screen", "provider", "dashboard"})


class ManifestError(ValueError):
    """A plugin manifest is invalid or incompatible."""


@dataclass(frozen=True)
class PluginManifest:
    plugin_id: str
    name: str
    version: str
    api_version: int
    capabilities: tuple[str, ...]
    entry_point: str
    description: str = ""


def parse_manifest(raw: Mapping[str, Any]) -> PluginManifest:
    """Validate metadata without loading plugin code or resolving paths."""
    if not isinstance(raw, Mapping):
        raise ManifestError("manifest must be a JSON object")
    plugin_id = raw.get("id")
    if not isinstance(plugin_id, str) or not _ID.fullmatch(plugin_id) or len(plugin_id) > 100:
        raise ManifestError("invalid plugin id")
    name = raw.get("name")
    if not isinstance(name, str) or not name.strip() or len(name) > 120:
        raise ManifestError("invalid plugin name")
    version = raw.get("version")
    if not isinstance(version, str) or not _VERSION.fullmatch(version):
        raise ManifestError("invalid plugin version")
    api_version = raw.get("api_version")
    if type(api_version) is not int or api_version != PLUGIN_API_VERSION:
        raise ManifestError("unsupported plugin API version")
    capabilities = raw.get("capabilities")
    if (not isinstance(capabilities, list) or not capabilities
            or any(not isinstance(c, str) or c not in _CAPABILITIES for c in capabilities)
            or len(set(capabilities)) != len(capabilities)):
        raise ManifestError("invalid plugin capabilities")
    entry_point = raw.get("entry_point")
    if (not isinstance(entry_point, str) or not re.fullmatch(
            r"[a-zA-Z_]\w*(?:\.[a-zA-Z_]\w*)*:[a-zA-Z_]\w*", entry_point)):
        raise ManifestError("invalid plugin entry point")
    description = raw.get("description", "")
    if not isinstance(description, str) or len(description) > 1000:
        raise ManifestError("invalid plugin description")
    unknown = set(raw) - {"id", "name", "version", "api_version", "capabilities", "entry_point", "description"}
    if unknown:
        raise ManifestError("unknown manifest fields: " + ", ".join(sorted(unknown)))
    return PluginManifest(plugin_id, name.strip(), version, api_version,
                          tuple(capabilities), entry_point, description)


def discover_plugins(directory: str | Path) -> tuple[dict[str, PluginManifest], dict[str, str]]:
    """Inspect immediate plugin subdirectories, returning valid entries and errors.

    Symlinked directories and manifest files are ignored to avoid following
    paths outside the configured plugin directory. No plugin code is imported.
    """
    root = Path(directory)
    found: dict[str, PluginManifest] = {}
    errors: dict[str, str] = {}
    if not root.exists():
        return found, errors
    if not root.is_dir() or root.is_symlink():
        raise ManifestError("plugin root must be a real directory")
    for folder in sorted(root.iterdir()):
        if folder.is_symlink() or not folder.is_dir():
            continue
        if not (folder / "uls-plugin.json").exists() and not (folder / "uls-plugin.toml").exists():
            continue
        try:
            manifest = load_plugin_manifest(folder)
            if folder.name != manifest.plugin_id:
                raise ManifestError("directory must match plugin id")
            if manifest.plugin_id in found:
                raise ManifestError("duplicate plugin id")
            found[manifest.plugin_id] = manifest
        except (ValueError, OSError, UnicodeError) as exc:
            errors[folder.name] = str(exc)
    return found, errors


def load_plugin_manifest(package: str | Path) -> PluginManifest:
    """Load native TOML or legacy JSON; reject ambiguous packages."""
    folder = Path(package)
    toml_path = folder / "uls-plugin.toml"
    json_path = folder / "uls-plugin.json"
    for path in (toml_path, json_path):
        if path.is_symlink():
            raise ManifestError("plugin manifest cannot be a symlink")
    if toml_path.is_file() and json_path.is_file():
        raise ManifestError("plugin must provide only one manifest format")
    path = toml_path if toml_path.is_file() else json_path
    if not path.is_file() or path.stat().st_size > 16384:
        raise ManifestError("missing or oversized native plugin manifest")
    try:
        content = path.read_text(encoding="utf-8")
        data = tomllib.loads(content) if path == toml_path else json.loads(content)
        return parse_manifest(data)
    except (ValueError, UnicodeError) as exc:
        raise ManifestError("invalid native plugin manifest") from exc
