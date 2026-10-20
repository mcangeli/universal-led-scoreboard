"""Read-only identification of standard MLB-LED-Scoreboard Bullpen packages.

This module intentionally does not import plugin code, install dependencies or
claim render compatibility. Actual rendering needs a separate graphics adapter.
"""
from __future__ import annotations

import configparser
import re
from dataclasses import dataclass
from pathlib import Path

BULLPEN_GROUP = "bullpen.mlbled.plugin"
_ENTRY = re.compile(r"^[a-zA-Z_]\w*(?:\.[a-zA-Z_]\w*)*:[a-zA-Z_]\w*$")


@dataclass(frozen=True)
class BullpenCandidate:
    name: str
    entry_point: str
    source: str


def detect_bullpen_package(directory: str | Path) -> tuple[BullpenCandidate, ...]:
    """Read setuptools entry points from a local pyproject.toml or setup.cfg.

    Do not execute setup.py or import modules. Dynamic metadata requires a
    separately approved inspection step.
    """
    root = Path(directory)
    if not root.is_dir() or root.is_symlink():
        return ()
    found = []
    pyproject = root / "pyproject.toml"
    if pyproject.is_file() and not pyproject.is_symlink():
        try:
            import tomllib
            with pyproject.open("rb") as stream:
                metadata = tomllib.load(stream)
            group = metadata.get("project", {}).get("entry-points", {}).get(BULLPEN_GROUP, {})
            if isinstance(group, dict):
                for name, target in group.items():
                    if isinstance(name, str) and isinstance(target, str) and _ENTRY.fullmatch(target):
                        found.append(BullpenCandidate(name, target, "pyproject.toml"))
        except (OSError, ValueError, TypeError):
            return ()
    cfg = root / "setup.cfg"
    if cfg.is_file() and not cfg.is_symlink():
        parser = configparser.ConfigParser(interpolation=None)
        try:
            parser.read(cfg, encoding="utf-8")
            if parser.has_option("options.entry_points", BULLPEN_GROUP):
                for line in parser.get("options.entry_points", BULLPEN_GROUP).splitlines():
                    if "=" not in line:
                        continue
                    name, target = (part.strip() for part in line.split("=", 1))
                    if name and _ENTRY.fullmatch(target):
                        found.append(BullpenCandidate(name, target, "setup.cfg"))
        except (OSError, configparser.Error):
            return tuple(found)
    return tuple(found)
