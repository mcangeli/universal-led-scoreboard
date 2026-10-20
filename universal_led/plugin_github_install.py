"""Install a GitHub plugin from an explicitly approved pinned review.

No third-party code is imported or executed.
"""
from __future__ import annotations

import json
import re
import tempfile
from pathlib import Path

from .plugin_download import download_github_plugin
from .plugin_install import install_local_plugin
from .plugin_manifest import ManifestError, parse_manifest
from .plugin_registry import parse_github_source
from .plugin_source import parse_plugin_source


def install_reviewed_github_plugin(source: str, commit: str, plugin_id: str,
                                   plugin_root="/var/lib/uls/plugins",
                                   registry_path="/var/lib/uls/plugins.json") -> dict:
    canonical, subpath = parse_plugin_source(source)
    owner, repo = parse_github_source(canonical)
    if not isinstance(commit, str) or not re.fullmatch(r"[0-9a-fA-F]{40}", commit):
        raise ManifestError("a pinned GitHub commit is required")
    if not isinstance(plugin_id, str) or not plugin_id:
        raise ManifestError("reviewed plugin ID is required")
    root = Path(plugin_root)
    registry = Path(registry_path)
    if not root.exists() and root.name == "plugins" and root.parent.is_dir() and not root.parent.is_symlink():
        root.mkdir(mode=0o700)
    canonical = f"https://github.com/{owner}/{repo}"
    with tempfile.TemporaryDirectory(prefix="uls-plugin-install-") as temp:
        package = download_github_plugin(canonical, commit, Path(temp) / "package")
        package = package / subpath if subpath else package
        manifest_file = package / "uls-plugin.json"
        if manifest_file.is_symlink() or not manifest_file.is_file() or manifest_file.stat().st_size > 16384:
            raise ManifestError("missing or unsafe plugin manifest")
        manifest = parse_manifest(json.loads(manifest_file.read_text(encoding="utf-8")))
        if manifest.plugin_id != plugin_id:
            raise ManifestError("reviewed plugin identity changed")
        return install_local_plugin(package, root, registry, source if subpath else canonical, commit)
