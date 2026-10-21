"""Read-only preview of a plugin hosted in a public GitHub repository.

No plugin code is imported or executed. A resolved commit is pinned for later
explicit installation; never trust an unpinned branch archive.
"""
from __future__ import annotations

import json
import re
from urllib.parse import quote
import tempfile
import urllib.request
from pathlib import Path

from .plugin_download import download_github_plugin
from .plugin_manifest import load_plugin_manifest
from .plugin_registry import parse_github_source
from .plugin_source import parse_plugin_source


def inspect_github_plugin(source_url: str) -> dict:
    canonical, subpath = parse_plugin_source(source_url)
    owner, repo = parse_github_source(canonical)
    branch = source_url.split("/tree/", 1)[1].rsplit("/plugins/", 1)[0] if subpath else "HEAD"
    url = f"https://api.github.com/repos/{owner}/{repo}/commits/{quote(branch, safe='')}"
    request = urllib.request.Request(url, headers={
        "User-Agent": "ULS-Plugin-Installer/0.9",
        "Accept": "application/vnd.github+json",
    })
    with urllib.request.urlopen(request, timeout=20) as response:
        raw = response.read(1024 * 1024 + 1)
    if len(raw) > 1024 * 1024:
        raise ValueError("GitHub commit response exceeds size limit")
    commit = json.loads(raw)["sha"]
    if not isinstance(commit, str) or not re.fullmatch(r"[0-9a-fA-F]{40}", commit):
        raise ValueError("GitHub returned an invalid commit SHA")
    with tempfile.TemporaryDirectory(prefix="uls-plugin-review-") as tmp:
        package = download_github_plugin(canonical, commit, Path(tmp) / "package")
        package = package / subpath if subpath else package
        manifest = load_plugin_manifest(package)
        return {
            "id": manifest.plugin_id, "name": manifest.name,
            "version": manifest.version, "description": manifest.description,
            "capabilities": list(manifest.capabilities),
            "source": source_url if subpath else canonical,
            "commit": commit,
            "enabled": False,
        }
