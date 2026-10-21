"""One-shot native plugin renderer. Writes raw 64x32 RGB to stdout."""
from __future__ import annotations
import importlib.util
import json
import sys
from pathlib import Path
from .display import Framebuffer
from .plugin_manifest import load_plugin_manifest


def main():
    if len(sys.argv) not in (3, 4):
        raise ValueError("expected plugin root and id")
    root, plugin_id = Path(sys.argv[1]), sys.argv[2]
    package = root / plugin_id
    if package.is_symlink() or not package.is_dir():
        raise ValueError("unsafe plugin directory")
    manifest = load_plugin_manifest(package)
    if manifest.plugin_id != plugin_id or "screen" not in manifest.capabilities:
        raise ValueError("invalid screen plugin")
    module_name, class_name = manifest.entry_point.split(":")
    source = package.joinpath(*module_name.split(".")).with_suffix(".py")
    if source.is_symlink() or not source.is_file() or not source.resolve().is_relative_to(package.resolve()):
        raise ValueError("unsafe plugin module")
    spec = importlib.util.spec_from_file_location("_uls_plugin_screen", source)
    if spec is None or spec.loader is None:
        raise ValueError("cannot load plugin module")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    instance = getattr(module, class_name)()
    if len(sys.argv) == 4:
        settings = json.loads(sys.argv[3])
        if not isinstance(settings, dict):
            raise ValueError('invalid plugin settings')
        configure = getattr(instance, 'configure', None)
        if callable(configure):
            configure(settings)
    frame = instance.render()
    if not isinstance(frame, Framebuffer) or (frame.width, frame.height) != (64, 32):
        raise ValueError("plugin must return a 64x32 Framebuffer")
    sys.stdout.buffer.write(bytes(channel for row in frame.pixels for pixel in row for channel in pixel))


if __name__ == "__main__":
    main()
