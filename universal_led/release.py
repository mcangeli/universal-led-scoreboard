"""Dashboard build identity from the installed Git checkout.

A preview label is not a release version: include the actual checked-out
commit so the UI reflects updates after pulling and restarting the service.
"""
from pathlib import Path
import subprocess

from . import __version__

PREVIEW = "0.6.0"
STAGE = 0


def installed_commit():
    root = Path(__file__).resolve().parent.parent
    try:
        result = subprocess.run(
            ['git', '-C', str(root), 'rev-parse', '--short=8', 'HEAD'],
            capture_output=True, text=True, timeout=2, check=False,
        )
    except (OSError, subprocess.TimeoutExpired):
        return None
    value = result.stdout.strip()
    return value if result.returncode == 0 and value else None


def display_version():
    commit = installed_commit()
    return f"v{__version__} · {commit}" if commit else f"v{__version__}"
