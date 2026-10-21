"""Official plugin discovery metadata; no plugin code is installed by discovery."""
from __future__ import annotations
import json
from pathlib import Path
from .plugin_manifest import ManifestError
from .plugin_source import parse_plugin_source


def read_official_catalog(path=None):
    if path is None:
        path = Path(__file__).resolve().parents[1] / "config" / "official-plugins.json"
    path = Path(path)
    if path.is_symlink() or not path.is_file() or path.stat().st_size > 65536:
        raise ManifestError("unsafe official plugin catalog")
    raw = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(raw, dict) or raw.get("schema_version") != 1 or not isinstance(raw.get("plugins"), list):
        raise ManifestError("invalid official plugin catalog")
    seen = set()
    result = []
    for entry in raw["plugins"]:
        if not isinstance(entry, dict) or set(entry) != {"id", "name", "description", "version", "source"}:
            raise ManifestError("invalid catalog entry")
        plugin_id = entry["id"]
        if not isinstance(plugin_id, str) or plugin_id in seen or plugin_id == "hello-world":
            raise ManifestError("duplicate or reserved catalog plugin")
        _, subpath = parse_plugin_source(entry["source"])
        if subpath != "plugins/" + plugin_id:
            raise ManifestError("catalog source does not match plugin id")
        for field in ("name", "description", "version"):
            if not isinstance(entry[field], str) or len(entry[field]) > 500:
                raise ManifestError("invalid catalog text")
        seen.add(plugin_id)
        result.append(dict(entry))
    return tuple(result)
