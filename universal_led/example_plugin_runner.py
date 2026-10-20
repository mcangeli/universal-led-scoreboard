"""Explicit, opt-in rendering of a bundled ULS example screen.

This is a developer diagnostic, NOT a general third-party plugin loader.
Only the repository-shipped Hello World example may execute here.
"""
from __future__ import annotations

import argparse
import importlib.util
from pathlib import Path

from .display import Framebuffer
from .frame_bridge import write_frame
from .plugin_manifest import parse_manifest
import json

EXAMPLE = Path(__file__).resolve().parents[1] / "plugins" / "hello-world"


def render_hello_world() -> Framebuffer:
    """Execute only the bundled example, after validating its manifest."""
    manifest = parse_manifest(json.loads((EXAMPLE / "uls-plugin.json").read_text(encoding="utf-8")))
    if manifest.plugin_id != "hello-world" or manifest.entry_point != "hello_world:HelloWorldScreen":
        raise ValueError("unexpected bundled example identity")
    source = EXAMPLE / "hello_world.py"
    if source.is_symlink() or not source.is_file():
        raise ValueError("bundled example source must be a regular file")
    spec = importlib.util.spec_from_file_location("_uls_bundled_hello_world", source)
    if spec is None or spec.loader is None:
        raise ValueError("unable to load bundled example")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    frame = module.HelloWorldScreen().render()
    if not isinstance(frame, Framebuffer) or (frame.width, frame.height) != (64, 32):
        raise ValueError("example must return a 64x32 Framebuffer")
    return frame


def main(argv=None):
    parser = argparse.ArgumentParser(description="Render bundled Hello World ULS plugin to PPM")
    parser.add_argument("--output", required=True, help="Output PPM path (not the live matrix frame)")
    args = parser.parse_args(argv)
    target = Path(args.output)
    write_frame(target, render_hello_world())
    print(f"Rendered bundled Hello World example to {target}")


if __name__ == "__main__":
    main()
