"""Update an installed plugin only from an explicitly approved GitHub commit."""
from __future__ import annotations

import json
import re
import tempfile
from pathlib import Path

from .plugin_download import download_github_plugin
from .plugin_manifest import ManifestError, parse_manifest
from .plugin_registry import parse_github_source, read_registry
from .plugin_source import parse_plugin_source
from .plugin_update import update_local_plugin


def update_reviewed_github_plugin(source: str, commit: str, plugin_id: str,
                                  plugin_root="/var/lib/uls/plugins",
                                  registry_path="/var/lib/uls/plugins.json", previous_source=None) -> dict:
    canonical, subpath = parse_plugin_source(source)
    owner, repo = parse_github_source(canonical)
    if not isinstance(commit, str) or not re.fullmatch(r"[0-9a-fA-F]{40}", commit):
        raise ManifestError("a pinned GitHub commit is required")
    root, registry = Path(plugin_root), Path(registry_path)
    installed = read_registry(registry)
    if plugin_id not in installed:
        raise ManifestError("reviewed plugin is not installed")
    old_source = installed[plugin_id]["source"]
    if previous_source is not None and previous_source != old_source:
        raise ManifestError("installed plugin source changed since review")
    if old_source != source:
        previous_repo, previous_path = parse_plugin_source(old_source)
        if previous_repo != canonical or previous_path or not subpath:
            # Cross-repository migration is only allowed to the official
            # catalog entry for this exact installed plugin ID.
            from .official_plugin_catalog import read_official_catalog
            approved = next((item for item in read_official_catalog()
                             if item["id"] == plugin_id and item["source"] == source), None)
            if approved is None:
                raise ManifestError("plugin source migration is not in official catalog")
    if installed[plugin_id]["commit"].lower() == commit.lower():
        raise ManifestError("plugin is already at the reviewed commit")
    with tempfile.TemporaryDirectory(prefix="uls-plugin-update-") as temp:
        package = download_github_plugin(f"https://github.com/{owner}/{repo}", commit, Path(temp) / "package")
        package = package / subpath if subpath else package
        manifest_file = package / "uls-plugin.json"
        if manifest_file.is_symlink() or not manifest_file.is_file() or manifest_file.stat().st_size > 16384:
            raise ManifestError("missing or unsafe plugin manifest")
        manifest = parse_manifest(json.loads(manifest_file.read_text(encoding="utf-8")))
        if manifest.plugin_id != plugin_id:
            raise ManifestError("reviewed plugin identity changed")
        return update_local_plugin(package, root, registry, source, commit)
