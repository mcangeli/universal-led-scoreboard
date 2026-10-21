"""Safe manual invalidation of per-plugin JSON data caches.

The plugin remains responsible for fetching fresh data on its next render.
No plugin Python code is invoked by this API.
"""
from pathlib import Path
import re


def invalidate_plugin_cache(plugin_id, root=Path("/var/lib/uls/plugin-cache")):
    if not isinstance(plugin_id, str) or not re.fullmatch(r"[a-z0-9]+(?:-[a-z0-9]+)*", plugin_id):
        raise ValueError("Invalid plugin ID")
    root = Path(root)
    directory = root / plugin_id
    if directory.is_symlink() or not directory.is_dir():
        return 0
    removed = 0
    for path in directory.iterdir():
        if path.is_symlink() or not path.is_file() or path.suffix != ".json":
            continue
        path.unlink()
        removed += 1
    return removed
