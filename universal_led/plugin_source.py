"""Parse GitHub plugin sources, including safe repository subdirectories."""
from __future__ import annotations

import re
from urllib.parse import urlsplit

from .plugin_manifest import ManifestError

_SEGMENT = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._-]*$")


def parse_plugin_source(url: str) -> tuple[str, str]:
    """Return canonical repository URL and safe relative plugin path.

    A tree URL may include a branch and a plugins/<name> directory. The
    branch is used only to locate the plugin; downloads are commit-pinned.
    """
    from .plugin_registry import parse_github_source
    try:
        owner, repo = parse_github_source(url)
        return f"https://github.com/{owner}/{repo}", ""
    except ManifestError:
        pass
    if not isinstance(url, str) or len(url) > 500:
        raise ManifestError("invalid GitHub plugin URL")
    parts = urlsplit(url)
    if parts.scheme != "https" or parts.netloc != "github.com" or parts.query or parts.fragment:
        raise ManifestError("invalid GitHub plugin URL")
    segments = parts.path.strip("/").split("/")
    if len(segments) < 6 or segments[2] != "tree" or segments[-2] != "plugins":
        raise ManifestError("expected GitHub repository or /tree/branch/plugins/name URL")
    owner, repo = parse_github_source("https://github.com/" + "/".join(segments[:2]))
    branch, name = "/".join(segments[3:-2]), segments[-1]
    if (not branch or any(not _SEGMENT.fullmatch(part) or part in {".", ".."} for part in segments[3:-2])
            or not _SEGMENT.fullmatch(name) or name in {".", ".."}):
        raise ManifestError("unsafe GitHub plugin path")
    return f"https://github.com/{owner}/{repo}", "plugins/" + name
