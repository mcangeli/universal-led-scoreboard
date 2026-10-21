"""Core-owned Google OAuth client configuration.

Administrators provision a public OAuth client ID in a private file.
The client ID is not a secret, but configuration remains outside plugin
settings and backups. Redirects are derived from an explicit HTTPS origin,
never from an untrusted Host or forwarded header.
"""
from __future__ import annotations

import json
from pathlib import Path
from urllib.parse import urlsplit


class OAuthConfigError(ValueError):
    pass


def load_google_client(path):
    path = Path(path)
    if path.is_symlink() or not path.is_file() or path.stat().st_size > 8192:
        raise OAuthConfigError("Google OAuth client not configured")
    try:
        config = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, ValueError):
        raise OAuthConfigError("Invalid Google OAuth configuration") from None
    if not isinstance(config, dict) or set(config) != {"client_id", "public_origin"}:
        raise OAuthConfigError("Invalid Google OAuth configuration")
    client_id, origin = config["client_id"], config["public_origin"]
    if not isinstance(client_id, str) or not client_id.endswith(".apps.googleusercontent.com"):
        raise OAuthConfigError("Invalid Google OAuth client ID")
    if not isinstance(origin, str):
        raise OAuthConfigError("Invalid OAuth public origin")
    parsed = urlsplit(origin)
    if (parsed.scheme != "https" or not parsed.hostname or parsed.username or
            parsed.password or parsed.path or parsed.query or parsed.fragment or
            origin.rstrip("/") != origin):
        raise OAuthConfigError("OAuth public origin must be an HTTPS origin")
    return {"client_id": client_id,
            "redirect_uri": origin + "/api/plugins/oauth/callback"}


def google_connection_status(config_path, vault, plugin_id="daily-calendar"):
    """Local desktop pairing needs no public HTTPS origin or Pi OAuth client.

    The legacy web-redirect configuration is not consulted for local pairing.
    """
    from .plugin_oauth_vault import VaultError
    try:
        credentials = vault.load(plugin_id)
        connected = bool(credentials.get("refresh_token"))
    except VaultError:
        connected = False
    return {"configured": True, "connected": connected, "method": "local-desktop-pairing"}
