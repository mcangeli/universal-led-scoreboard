"""Safe GitHub plugin source parsing and on-disk registry primitives.

No network access, package execution, or installation occurs here. These
functions validate identities before the future privileged installer runs.
"""
from __future__ import annotations

import json
import re
from pathlib import Path
from urllib.parse import urlsplit

from .plugin_manifest import ManifestError, parse_manifest

_OWNER_RE = re.compile(r"^[A-Za-z0-9](?:[A-Za-z0-9-]{0,37}[A-Za-z0-9])?$")
_REPO_RE = re.compile(r"^[A-Za-z0-9_.-]{1,100}$")


def parse_github_source(url: str) -> tuple[str, str]:
    """Accept only canonical public GitHub HTTPS repository URLs."""
    if not isinstance(url, str) or len(url) > 300:
        raise ManifestError("invalid GitHub repository URL")
    parts = urlsplit(url)
    if (parts.scheme != "https" or parts.netloc != "github.com"
            or parts.username or parts.password or parts.query or parts.fragment):
        raise ManifestError("GitHub source must use https://github.com/owner/repo")
    path = parts.path.removesuffix("/")
    if path.endswith(".git"):
        path = path[:-4]
    segments = path.split("/")
    if (len(segments) != 3 or segments[0] != ""
            or not _OWNER_RE.fullmatch(segments[1])
            or not _REPO_RE.fullmatch(segments[2])
            or segments[2] in {".", ".."}):
        raise ManifestError("invalid GitHub owner or repository")
    return segments[1], segments[2]


def registry_record(manifest_data: dict, source_url: str, commit: str) -> dict:
    """Validate installation metadata before it is persisted."""
    manifest = parse_manifest(manifest_data)
    owner, repo = parse_github_source(source_url)
    if not isinstance(commit, str) or not re.fullmatch(r"[0-9a-fA-F]{40}", commit):
        raise ManifestError("plugin source must be pinned to a 40-character commit")
    return {
        "id": manifest.plugin_id,
        "version": manifest.version,
        "source": f"https://github.com/{owner}/{repo}",
        "commit": commit.lower(),
        "enabled": False,
    }


def read_registry(path: str | Path) -> dict[str, dict]:
    """Read a registry without following symlinks or executing plugin code."""
    path = Path(path)
    if not path.exists():
        return {}
    if path.is_symlink() or not path.is_file() or path.stat().st_size > 1024 * 1024:
        raise ManifestError("unsafe plugin registry file")
    try:
        raw = json.loads(path.read_text(encoding="utf-8"))
    except (ValueError, UnicodeError) as exc:
        raise ManifestError("invalid plugin registry JSON") from exc
    if not isinstance(raw, dict):
        raise ManifestError("plugin registry must be an object")
    result = {}
    for key, value in raw.items():
        if not isinstance(value, dict) or key != value.get("id"):
            raise ManifestError("invalid plugin registry entry")
        expected = registry_record(
            {"id": key, "name": key, "version": value.get("version"),
             "api_version": 1, "capabilities": ["screen"],
             "entry_point": "plugin:Plugin"},
            value.get("source"), value.get("commit"))
        if type(value.get("enabled")) is not bool or set(value) != set(expected):
            raise ManifestError("invalid plugin registry fields")
        result[key] = dict(value)
    return result
