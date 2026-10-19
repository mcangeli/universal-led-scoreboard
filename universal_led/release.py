"""Installed build identity for the dashboard, derived from Git metadata."""
from pathlib import Path
import subprocess

from . import __version__


def _git(*args):
    root = Path(__file__).resolve().parent.parent
    try:
        result = subprocess.run(
            ['git', '-C', str(root), *args],
            capture_output=True, text=True, timeout=2, check=False)
    except (OSError, subprocess.TimeoutExpired):
        return None
    value = result.stdout.strip()
    return value if result.returncode == 0 and value else None


def installed_commit():
    return _git('rev-parse', '--short=8', 'HEAD')


def installed_release():
    """Identify exact tagged releases, otherwise show the development channel."""
    tag = _git('describe', '--tags', '--exact-match')
    if tag:
        return tag
    branch = _git('symbolic-ref', '--quiet', '--short', 'HEAD')
    if branch and branch != 'HEAD':
        return branch
    # Updater installations can be detached; a matching remote branch is
    # useful only when it points at this exact commit.
    refs = _git('branch', '-r', '--points-at', 'HEAD')
    if refs:
        names = [line.strip() for line in refs.splitlines()]
        if 'origin/main' in names:
            return 'main'
        for name in names:
            if name.startswith('origin/feature/'):
                return name[len('origin/'):]
    return 'development'


def display_version():
    commit = installed_commit()
    label = f"v{__version__} · {installed_release()}"
    return f"{label} · {commit}" if commit else label
