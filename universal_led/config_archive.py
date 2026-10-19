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


MAX_ARCHIVE_BYTES = 8 * 1024 * 1024


def inspect_portable(archive_bytes: bytes, destination: str | Path) -> dict:
    """Validate an archive and preview differences; never write to destination.

    An archive containing any non-allowlisted file, including hardware settings,
    is rejected instead of quietly discarding the unexpected entry.
    """
    if not isinstance(archive_bytes, bytes) or len(archive_bytes) > MAX_ARCHIVE_BYTES:
        raise ValueError("Invalid or oversized configuration archive")
    try:
        with zipfile.ZipFile(io.BytesIO(archive_bytes)) as archive:
            members = archive.infolist()
            names = [member.filename for member in members]
            if len(names) != len(set(names)):
                raise ValueError("Duplicate archive members")
            allowed = {"manifest.json"} | {section + ".json" for section in PORTABLE_SECTIONS}
            if "manifest.json" not in names or set(names) - allowed:
                raise ValueError("Archive contains unknown or device-specific files")
            if any(member.is_dir() or member.file_size > MAX_SECTION_BYTES or
                   member.flag_bits & 0x1 for member in members):
                raise ValueError("Unsupported archive member")
            manifest = json.loads(archive.read("manifest.json"))
            if not isinstance(manifest, dict) or manifest.get("format_version") != FORMAT_VERSION or (
                manifest.get("kind") != "portable-application-settings"
            ):
                raise ValueError("Unsupported portable archive format")
            sections = manifest.get("sections")
            if not isinstance(sections, dict) or set(sections) != set(names) - {"manifest.json"}:
                raise ValueError("Archive manifest does not match contents")
            destination_root = Path(destination)
            preview = {}
            for name in sorted(sections):
                info = sections[name]
                data = archive.read(name)
                if not isinstance(info, dict) or info.get("bytes") != len(data) or (
                    info.get("sha256") != hashlib.sha256(data).hexdigest()
                ):
                    raise ValueError("Archive checksum mismatch: " + name)
                value = json.loads(data)
                if not isinstance(value, dict):
                    raise ValueError("Invalid configuration section: " + name)
                target = destination_root / name
                if target.is_symlink():
                    raise ValueError("Destination configuration is symlinked: " + name)
                current = json.loads(target.read_text(encoding="utf-8")) if target.is_file() else None
                preview[name.removesuffix(".json")] = {
                    "action": "unchanged" if current == value else ("replace" if current is not None else "add"),
                    "exists_on_destination": current is not None,
                }
            return {
                "format_version": FORMAT_VERSION,
                "sections": preview,
                "hardware_preserved": True,
                "applied": False,
            }
    except (zipfile.BadZipFile, UnicodeDecodeError, KeyError, TypeError, json.JSONDecodeError) as exc:
        raise ValueError("Invalid configuration archive") from exc


def validate_portable_sections(archive_bytes: bytes, destination: str | Path) -> dict:
    """Perform schema checks after integrity inspection, without writing files.

    Legacy optional fields are normalized using the application's validators.
    Device-specific settings are never eligible for this operation.
    """
    preview = inspect_portable(archive_bytes, destination)
    from .sport_settings import validate_settings
    from .colors import normalize_team_colors, normalize_scoreboard_colors
    from .nhl_colors import NHL_TEAM_COLORS
    from .time_weather_settings import validate_time_weather
    from .season_countdown_settings import validate as validate_countdown
    validators = {
        "settings": validate_settings,
        "teams": normalize_team_colors,
        "nhl_teams": normalize_team_colors,
        "scoreboard": normalize_scoreboard_colors,
        "time_weather": validate_time_weather,
        "season_countdown": validate_countdown,
    }
    with zipfile.ZipFile(io.BytesIO(archive_bytes)) as archive:
        for section in preview["sections"]:
            value = json.loads(archive.read(section + ".json"))
            validators[section](value)
            if section == "nhl_teams" and set(value) - set(NHL_TEAM_COLORS):
                raise ValueError("Unknown NHL team color keys")
    preview["schema_valid"] = True
    return preview


def restore_portable(archive_bytes: bytes, destination: str | Path, sections: list[str]) -> dict:
    """Restore explicitly selected sections with rollback on write failure.

    Validation happens before writes. Every original file is retained in a
    local recovery directory, and originals are restored if a write fails.
    """
    import os
    import tempfile
    from uuid import uuid4

    preview = validate_portable_sections(archive_bytes, destination)
    if not isinstance(sections, list) or not sections or len(sections) != len(set(sections)):
        raise ValueError("Select one or more distinct sections")
    if any(type(section) is not str or section not in preview["sections"] for section in sections):
        raise ValueError("Unknown or unapproved restore section")
    root = Path(destination)
    root.mkdir(parents=True, exist_ok=True)
    recovery = root / "backups" / ("portable-restore-" + uuid4().hex)
    recovery.mkdir(parents=True, exist_ok=False)
    originals = {}
    applied = []
    try:
        with zipfile.ZipFile(io.BytesIO(archive_bytes)) as archive:
            for section in sections:
                target = root / (section + ".json")
                originals[section] = target.read_bytes() if target.exists() else None
                if originals[section] is not None:
                    (recovery / (section + ".json")).write_bytes(originals[section])
            for section in sections:
                target = root / (section + ".json")
                payload = archive.read(section + ".json")
                fd, tmp = tempfile.mkstemp(prefix=".portable-", dir=root)
                try:
                    with os.fdopen(fd, "wb") as stream:
                        stream.write(payload)
                        stream.flush()
                        os.fsync(stream.fileno())
                    os.replace(tmp, target)
                    applied.append(section)
                    if target.read_bytes() != payload:
                        raise OSError('Restore verification failed: ' + section)
                finally:
                    if os.path.exists(tmp):
                        os.unlink(tmp)
    except Exception:
        for section in reversed(applied):
            target = root / (section + ".json")
            previous = originals[section]
            if previous is None:
                target.unlink(missing_ok=True)
            else:
                fd, tmp = tempfile.mkstemp(prefix=".portable-rollback-", dir=root)
                try:
                    with os.fdopen(fd, "wb") as stream:
                        stream.write(previous)
                        stream.flush()
                        os.fsync(stream.fileno())
                    os.replace(tmp, target)
                finally:
                    if os.path.exists(tmp):
                        os.unlink(tmp)
        raise
    return {"applied": True, "verified": True, "sections": applied,
            "hardware_preserved": True, "restart_required": True,
            "recovery_directory": str(recovery)}
