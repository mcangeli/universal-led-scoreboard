"""Read-only preview of a plugin hosted in a public GitHub repository.

No plugin code is imported or executed. A resolved commit is pinned for later
explicit installation; never trust an unpinned branch archive.
"""
from __future__ import annotations

import json
import tempfile
import urllib.request
from pathlib import Path

from .plugin_download import download_github_plugin
from .plugin_manifest import parse_manifest
from .plugin_registry import parse_github_source
from .plugin_source import parse_plugin_source


def inspect_github_plugin(source_url: str) -> dict:
    canonical, subpath = parse_plugin_source(source_url)
    owner, repo = parse_github_source(canonical)
    url = f"https://api.github.com/repos/{owner}/{repo}/commits/HEAD"
    request = urllib.request.Request(url, headers={
        "User-Agent": "ULS-Plugin-Installer/0.9",
        "Accept": "application/vnd.github+json",
    })
    with urllib.request.urlopen(request, timeout=20) as response:
        raw = response.read(1024 * 1024 + 1)
    if len(raw) > 1024 * 1024:
        raise ValueError("GitHub commit response exceeds size limit")
    commit = json.loads(raw)["sha"]
    with tempfile.TemporaryDirectory(prefix="uls-plugin-review-") as tmp:
        package = download_github_plugin(source_url, commit, Path(tmp) / "package")
        package = package / subpath if subpath else package
        manifest_file = package / "uls-plugin.json"
        if manifest_file.is_symlink() or not manifest_file.is_file():
            raise ValueError("GitHub repository must contain uls-plugin.json at its root")
        if manifest_file.stat().st_size > 16384:
            raise ValueError("plugin manifest exceeds size limit")
        manifest = parse_manifest(json.loads(manifest_file.read_text(encoding="utf-8")))
        return {
            "id": manifest.plugin_id, "name": manifest.name,
            "version": manifest.version, "description": manifest.description,
            "capabilities": list(manifest.capabilities),
            "source": source_url if subpath else canonical,
            "commit": commit,
            "enabled": False,
        }
