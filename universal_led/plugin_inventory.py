"""Read-only installed-plugin inventory for dashboard and diagnostics.

Inventory never imports third-party code and never mutates plugin settings.
"""
from __future__ import annotations

from pathlib import Path

from .plugin_manifest import discover_plugins, ManifestError
from .plugin_registry import read_registry


def installed_plugin_inventory(plugin_root: str | Path, registry_path: str | Path) -> dict:
    """Return stable, JSON-serializable installed entries and discovery errors."""
    registered = read_registry(registry_path)
    discovered, errors = discover_plugins(plugin_root)
    items = []
    for plugin_id, record in sorted(registered.items()):
        manifest = discovered.get(plugin_id)
        problem = errors.get(plugin_id)
        if manifest is None and problem is None:
            problem = "installed package or manifest is missing"
        elif manifest is not None and manifest.version != record["version"]:
            problem = "installed package version does not match registry"
        items.append({
            "id": plugin_id,
            "name": manifest.name if manifest else plugin_id,
            "version": record["version"],
            "enabled": record["enabled"],
            "source": record["source"],
            "commit": record["commit"],
            "capabilities": list(manifest.capabilities) if manifest else [],
            "status": "error" if problem else ("enabled" if record["enabled"] else "disabled"),
            "error": problem,
        })
    unregistered = sorted(set(discovered) - set(registered))
    return {
        "plugins": items,
        "errors": dict(sorted(errors.items())),
        "unregistered": unregistered,
    }
