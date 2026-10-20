"""Explicit installer for the bundled Hello World example.

Run with permissions to write the ULS persistent plugin directory. Never
activates the plugin, restarts services, or executes its renderer.
"""
from __future__ import annotations

import argparse
from pathlib import Path

from .plugin_install import install_local_plugin

EXAMPLE = Path(__file__).resolve().parents[1] / "plugins" / "hello-world"
SOURCE = "https://github.com/mcangeli/universal-led-scoreboard"
PINNED_EXAMPLE_COMMIT = "0c214f677cf71dc43abc2ff2042eea4001bfdd01"


def install_example(root="/var/lib/uls/plugins", registry="/var/lib/uls/plugins.json"):
    """Register a copy of the bundled example, disabled by default."""
    root = Path(root)
    registry = Path(registry)
    # First-use bootstrap: only create the expected plugins directory, never
    # create arbitrary parent paths or change existing ownership.
    if not root.exists() and root.name == "plugins" and root.parent.is_dir() and not root.parent.is_symlink():
        root.mkdir(mode=0o700)
    return install_local_plugin(EXAMPLE, root, registry, SOURCE, PINNED_EXAMPLE_COMMIT)


def main(argv=None):
    parser = argparse.ArgumentParser(description="Install bundled Hello World as disabled managed ULS plugin")
    parser.add_argument("--plugin-root", default="/var/lib/uls/plugins")
    parser.add_argument("--registry", default="/var/lib/uls/plugins.json")
    args = parser.parse_args(argv)
    record = install_example(args.plugin_root, args.registry)
    print(f"Installed {record['id']} v{record['version']} (disabled). Live rotation unchanged.")


if __name__ == "__main__":
    main()
