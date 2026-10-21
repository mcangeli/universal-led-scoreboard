"""Transactional installation of already-downloaded ULS plugin directories.

Network fetching and trust approval belong to a separate privileged workflow.
This module never imports or executes third-party plugin code.
"""
from __future__ import annotations

import json
import os
import shutil
import tempfile
from pathlib import Path

from .plugin_manifest import ManifestError, load_plugin_manifest
from .plugin_registry import read_registry, registry_record


def install_local_plugin(package_dir, plugin_root, registry_path, source_url, commit):
    """Stage, validate, and install an unpacked package without running code.

    Reject symlinks and special files. Existing plugin IDs are deliberately
    refused until a separate transactional update/rollback path is available.
    """
    source = Path(package_dir)
    root = Path(plugin_root)
    registry = Path(registry_path)
    if not source.is_dir() or source.is_symlink():
        raise ManifestError("plugin package must be a real directory")
    if not root.is_dir() or root.is_symlink():
        raise ManifestError("plugin installation root must be a real directory")
    if not registry.parent.is_dir() or registry.parent.is_symlink():
        raise ManifestError("registry parent must be a real directory")
    if registry.is_symlink():
        raise ManifestError("registry cannot be a symlink")
    manifest = load_plugin_manifest(source)
    manifest_data = {"id": manifest.plugin_id, "name": manifest.name, "version": manifest.version, "api_version": manifest.api_version, "capabilities": list(manifest.capabilities), "entry_point": manifest.entry_point, "description": manifest.description}
    record = registry_record(manifest_data, source_url, commit)
    plugin_id = record["id"]
    destination = root / plugin_id
    entries = read_registry(registry)
    if plugin_id in entries or destination.exists() or destination.is_symlink():
        raise ManifestError("plugin is already installed")
    if registry.exists() and not registry.is_file():
        raise ManifestError("invalid registry destination")

    # Never copy links, sockets, device files, or nested mount-like surprises.
    for base, dirs, files in os.walk(source, followlinks=False):
        for name in dirs + files:
            entry = Path(base) / name
            if entry.is_symlink() or not (entry.is_file() or entry.is_dir()):
                raise ManifestError("plugin package contains unsafe filesystem entries")

    stage = Path(tempfile.mkdtemp(prefix=".uls-plugin-", dir=root))
    try:
        shutil.copytree(source, stage / "package", symlinks=False)
        staged = stage / "package"
        # Revalidate staged metadata before publication.
        if load_plugin_manifest(staged).plugin_id != plugin_id:
            raise ManifestError("staged plugin identity mismatch")
        entries[plugin_id] = record
        fd, tmpname = tempfile.mkstemp(prefix=".uls-registry-", dir=registry.parent)
        try:
            with os.fdopen(fd, "w", encoding="utf-8") as handle:
                json.dump(entries, handle, indent=2, sort_keys=True)
                handle.write("\n")
                handle.flush()
                os.fsync(handle.fileno())
            os.replace(staged, destination)
            try:
                os.replace(tmpname, registry)
            except Exception:
                shutil.rmtree(destination)
                raise
        finally:
            if os.path.exists(tmpname):
                os.unlink(tmpname)
    finally:
        shutil.rmtree(stage, ignore_errors=True)
    return record
