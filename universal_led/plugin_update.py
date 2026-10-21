"""Transactional replacement of installed native plugins, preserving external data."""
from __future__ import annotations

import json
import os
import shutil
import tempfile
from pathlib import Path

from .plugin_manifest import ManifestError, parse_manifest
from .plugin_registry import read_registry, registry_record


def update_local_plugin(package_dir, plugin_root, registry_path, source_url, commit):
    source, root, registry = Path(package_dir), Path(plugin_root), Path(registry_path)
    if (not source.is_dir() or source.is_symlink() or not root.is_dir()
            or root.is_symlink() or not registry.is_file() or registry.is_symlink()
            or registry.parent.is_symlink()):
        raise ManifestError("unsafe plugin update paths")
    manifest_path = source / "uls-plugin.json"
    if manifest_path.is_symlink() or not manifest_path.is_file() or manifest_path.stat().st_size > 16384:
        raise ManifestError("unsafe update manifest")
    manifest_data = json.loads(manifest_path.read_text(encoding="utf-8"))
    manifest = parse_manifest(manifest_data)
    records = read_registry(registry)
    if manifest.plugin_id not in records:
        raise ManifestError("plugin is not installed")
    old = records[manifest.plugin_id]
    if old["source"] != source_url:
        # Allow migration from a legacy repository-root source to a reviewed
        # plugin subdirectory in that SAME repository, never across repos.
        from .plugin_source import parse_plugin_source
        previous_repo, previous_path = parse_plugin_source(old["source"])
        proposed_repo, proposed_path = parse_plugin_source(source_url)
        if previous_repo != proposed_repo or previous_path or not proposed_path:
            raise ManifestError("plugin source changed; refusing update")
    destination = root / manifest.plugin_id
    if not destination.is_dir() or destination.is_symlink():
        raise ManifestError("unsafe installed plugin directory")
    for base, dirs, files in os.walk(source, followlinks=False):
        for name in dirs + files:
            entry = Path(base) / name
            if entry.is_symlink() or not (entry.is_file() or entry.is_dir()):
                raise ManifestError("unsafe update package entry")
    record = registry_record(manifest_data, source_url, commit)
    record["enabled"] = old["enabled"]
    stage = Path(tempfile.mkdtemp(prefix=".uls-update-", dir=root))
    temporary_registry = None
    swapped = False
    published = False
    try:
        staged = stage / "new"
        shutil.copytree(source, staged)
        if parse_manifest(json.loads((staged / "uls-plugin.json").read_text(encoding="utf-8"))).plugin_id != manifest.plugin_id:
            raise ManifestError("staged plugin identity mismatch")
        records[manifest.plugin_id] = record
        fd, temporary_registry = tempfile.mkstemp(prefix=".uls-registry-", dir=registry.parent)
        with os.fdopen(fd, "w", encoding="utf-8") as handle:
            json.dump(records, handle, indent=2, sort_keys=True)
            handle.write("\n")
            handle.flush()
            os.fsync(handle.fileno())
        destination.rename(stage / "old")
        try:
            staged.rename(destination)
            swapped = True
            os.replace(temporary_registry, registry)
            temporary_registry = None
            published = True
        except Exception:
            if swapped:
                destination.rename(stage / "failed")
            (stage / "old").rename(destination)
            raise
    finally:
        if temporary_registry and os.path.exists(temporary_registry):
            os.unlink(temporary_registry)
        if published:
            shutil.rmtree(stage, ignore_errors=True)
        elif (stage / "old").exists():
            # Never delete the only remaining copy if recovery was interrupted.
            pass
        else:
            shutil.rmtree(stage, ignore_errors=True)
    return record
