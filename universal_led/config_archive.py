"""Portable configuration archive foundation.

Export is deliberately allowlisted. Hardware, identity and credentials never
enter a portable archive, even when stored next to application configuration.
"""
from __future__ import annotations

import hashlib
import io
import json
import zipfile
from datetime import datetime, timezone
from pathlib import Path

PORTABLE_SECTIONS = (
    "settings", "teams", "nhl_teams", "scoreboard",
    "time_weather", "season_countdown",
)
FORMAT_VERSION = 1
MAX_SECTION_BYTES = 1024 * 1024


def export_portable(directory: str | Path) -> bytes:
    """Return a ZIP containing only approved, validated application JSON files.

    This API does not import, apply, or modify any destination settings.
    """
    root = Path(directory)
    entries = {}
    for section in PORTABLE_SECTIONS:
        path = root / (section + ".json")
        if not path.is_file():
            continue
        if path.is_symlink():
            raise ValueError("Refusing symlinked configuration: " + section)
        data = path.read_bytes()
        if len(data) > MAX_SECTION_BYTES:
            raise ValueError("Configuration section too large: " + section)
        decoded = json.loads(data)
        if not isinstance(decoded, dict):
            raise ValueError("Configuration section must be an object: " + section)
        entries[section + ".json"] = data
    manifest = {
        "format_version": FORMAT_VERSION,
        "kind": "portable-application-settings",
        "created_at": datetime.now(timezone.utc).isoformat(),
        "sections": {
            name: {"sha256": hashlib.sha256(data).hexdigest(), "bytes": len(data)}
            for name, data in sorted(entries.items())
        },
        "excluded": ["hardware", "matrix", "network", "authentication", "secrets"],
    }
    buffer = io.BytesIO()
    with zipfile.ZipFile(buffer, "w", compression=zipfile.ZIP_DEFLATED) as archive:
        archive.writestr("manifest.json", json.dumps(manifest, indent=2) + "\n")
        for name, data in sorted(entries.items()):
            archive.writestr(name, data)
    return buffer.getvalue()
