"""Core-owned private OAuth token vault for trusted provider integrations.

This vault is intentionally independent of portable plugin settings. The
configurator must authenticate and authorize any caller before using it.
"""
from __future__ import annotations

import json
import os
from pathlib import Path
import re
import tempfile

_ID = re.compile(r"^[a-z][a-z0-9]*(?:[._-][a-z0-9]+)*$")


class VaultError(ValueError):
    pass


class PluginTokenVault:
    def __init__(self, root):
        self.root = Path(root)

    def _directory(self):
        if self.root.is_symlink():
            raise VaultError("OAuth vault cannot be a symlink")
        self.root.mkdir(parents=True, exist_ok=True, mode=0o700)
        if not self.root.is_dir() or self.root.stat().st_mode & 0o077:
            raise VaultError("OAuth vault directory must be private")
        return self.root

    def _path(self, plugin_id):
        if not isinstance(plugin_id, str) or len(plugin_id) > 100 or not _ID.fullmatch(plugin_id):
            raise VaultError("Invalid plugin ID")
        return self._directory() / (plugin_id + ".json")

    def save(self, plugin_id, credentials):
        path = self._path(plugin_id)
        if path.is_symlink():
            raise VaultError("OAuth credential file cannot be a symlink")
        if not isinstance(credentials, dict) or not credentials.get("refresh_token"):
            raise VaultError("OAuth refresh token required")
        fd, temporary = tempfile.mkstemp(prefix=".oauth-", dir=self.root)
        try:
            with os.fdopen(fd, "w", encoding="utf-8") as stream:
                os.fchmod(stream.fileno(), 0o600)
                json.dump(credentials, stream)
                stream.flush()
                os.fsync(stream.fileno())
            os.replace(temporary, path)
        finally:
            if os.path.exists(temporary):
                os.unlink(temporary)

    def load(self, plugin_id):
        path = self._path(plugin_id)
        if path.is_symlink():
            raise VaultError("OAuth credential file cannot be a symlink")
        try:
            if path.stat().st_mode & 0o077:
                raise VaultError("OAuth credential file must be private")
            with path.open(encoding="utf-8") as stream:
                result = json.load(stream)
        except (OSError, ValueError) as exc:
            if isinstance(exc, VaultError):
                raise
            raise VaultError("OAuth credentials unavailable") from None
        if not isinstance(result, dict) or not result.get("refresh_token"):
            raise VaultError("Invalid OAuth credentials")
        return result

    def delete(self, plugin_id):
        path = self._path(plugin_id)
        if path.is_symlink():
            raise VaultError("OAuth credential file cannot be a symlink")
        path.unlink(missing_ok=True)
