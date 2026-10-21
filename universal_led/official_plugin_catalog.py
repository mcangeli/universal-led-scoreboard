"""Official plugin discovery metadata; no plugin code is installed by discovery."""
from __future__ import annotations
import json
import os
import time
from urllib.request import Request, urlopen
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

# The official repository owns publication metadata. A bundled snapshot is the
# offline fallback, not the authoritative list after a successful refresh.
REMOTE_CATALOG_URL = "https://raw.githubusercontent.com/mcangeli/uls-plugins/main/catalog.json"
CACHE_SECONDS = 15 * 60
MAX_CATALOG_BYTES = 65536


def dynamic_official_catalog(*, cache_path=None, refresh=False, fetch=None, now=None):
    """Return validated remote entries, using disk cache or bundled fallback.

    Never execute code from the catalog. GitHub plugin installation still goes
    through the existing pinned-commit review flow.
    """
    if cache_path is None:
        cache_path = Path("/var/lib/uls/official-plugins-cache.json")
    cache_path = Path(cache_path)
    now = time.time() if now is None else now
    fallback = read_official_catalog()
    try:
        cached = read_official_catalog(cache_path)
    except (OSError, ValueError, TypeError):
        cached = None
    try:
        fresh = now - cache_path.stat().st_mtime < CACHE_SECONDS
    except OSError:
        fresh = False
    if cached is not None and fresh and not refresh:
        return cached, "cache"
    try:
        if fetch is None:
            request = Request(REMOTE_CATALOG_URL, headers={"User-Agent": "ULS-Plugin-Catalog/0.9"})
            with urlopen(request, timeout=3) as response:
                raw = response.read(MAX_CATALOG_BYTES + 1)
        else:
            raw = fetch()
        if len(raw) > MAX_CATALOG_BYTES:
            raise ManifestError("official catalog exceeds size limit")
        cache_path.parent.mkdir(parents=True, exist_ok=True)
        # Validate untrusted bytes before writing the persistent cache.
        import tempfile
        with tempfile.NamedTemporaryFile(dir=cache_path.parent, delete=False) as temp:
            temp.write(raw)
            candidate = Path(temp.name)
        try:
            validated = read_official_catalog(candidate)
            os.chmod(candidate, 0o600)
            os.replace(candidate, cache_path)
        finally:
            candidate.unlink(missing_ok=True)
        return validated, "remote"
    except (OSError, ValueError, TypeError):
        return (cached, "stale-cache") if cached is not None else (fallback, "bundled-fallback")
