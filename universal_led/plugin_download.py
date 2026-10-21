"""Download a pinned GitHub plugin snapshot with strict archive validation.

Retrieval does not execute plugin code. The caller must explicitly authorize
installation after reviewing the source and manifest.
"""
from __future__ import annotations

import io
import re
import tarfile
import urllib.request
from pathlib import Path

from .plugin_manifest import ManifestError
from .plugin_registry import parse_github_source

MAX_ARCHIVE_BYTES = 20 * 1024 * 1024
MAX_UNPACKED_BYTES = 40 * 1024 * 1024
MAX_FILES = 2000


def extract_github_archive(archive: bytes, destination: str | Path) -> Path:
    """Extract a GitHub tarball to an empty destination, rejecting unsafe entries."""
    destination = Path(destination)
    if destination.exists():
        raise ManifestError("archive destination already exists")
    if len(archive) > MAX_ARCHIVE_BYTES:
        raise ManifestError("plugin archive exceeds size limit")
    files = []
    total = 0
    try:
        with tarfile.open(fileobj=io.BytesIO(archive), mode="r:gz") as tar:
            for member in tar:
                parts = Path(member.name).parts
                if (not parts or any(part in ("", ".", "..") for part in parts)
                        or member.name.startswith("/") or "\\" in member.name
                        or not (member.isfile() or member.isdir())):
                    raise ManifestError("unsafe plugin archive entry")
                if member.isfile():
                    total += member.size
                    files.append((member, parts))
                if total > MAX_UNPACKED_BYTES or len(files) > MAX_FILES:
                    raise ManifestError("plugin archive exceeds unpacked limits")
            roots = {parts[0] for _, parts in files}
            if len(roots) != 1 or not files:
                raise ManifestError("archive must contain one package root")
            root = next(iter(roots))
            destination.mkdir(parents=True)
            for member, parts in files:
                relative = parts[1:]
                if not relative:
                    raise ManifestError("archive contains root-level file")
                target = destination.joinpath(*relative)
                target.parent.mkdir(parents=True, exist_ok=True)
                stream = tar.extractfile(member)
                if stream is None:
                    raise ManifestError("unreadable archive entry")
                with stream, target.open("xb") as out:
                    remaining = member.size
                    while remaining:
                        chunk = stream.read(min(65536, remaining))
                        if not chunk:
                            raise ManifestError("truncated archive entry")
                        out.write(chunk)
                        remaining -= len(chunk)
    except (tarfile.TarError, OSError, EOFError) as exc:
        raise ManifestError("invalid plugin archive") from exc
    return destination


def download_github_plugin(source_url: str, commit: str, destination: str | Path) -> Path:
    """Download only a pinned GitHub commit through GitHub's archive endpoint."""
    owner, repo = parse_github_source(source_url)
    if not isinstance(commit, str) or not re.fullmatch(r"[0-9a-fA-F]{40}", commit):
        raise ManifestError("GitHub archive must be pinned to a full commit SHA")
    url = f"https://api.github.com/repos/{owner}/{repo}/tarball/{commit.lower()}"
    request = urllib.request.Request(url, headers={"User-Agent": "ULS-Plugin-Installer/0.9"})
    with urllib.request.urlopen(request, timeout=30) as response:
        archive = response.read(MAX_ARCHIVE_BYTES + 1)
    return extract_github_archive(archive, destination)
