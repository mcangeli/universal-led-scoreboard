"""Google OAuth token exchange for Core's trusted provider integration.

The transport accepts only the fixed Google token endpoint and never places
authorization codes or refresh tokens in URLs, logs or plugin settings.
"""
from __future__ import annotations

import json
import time
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode
from urllib.request import Request, urlopen

from .plugin_oauth_providers import resolve_provider


class TokenExchangeError(ValueError):
    pass


def exchange_google_code(client_id, callback, opener=urlopen, clock=time.time):
    provider = resolve_provider("daily-calendar", "google-calendar")
    fields = {"client_id": client_id, "code": callback["code"],
              "code_verifier": callback["code_verifier"],
              "redirect_uri": callback["redirect_uri"],
              "grant_type": "authorization_code"}
    request = Request(provider.token_endpoint, data=urlencode(fields).encode("utf-8"),
                      headers={"Content-Type": "application/x-www-form-urlencoded"},
                      method="POST")
    try:
        with opener(request, timeout=8) as response:
            payload = response.read(65537)
    except (HTTPError, URLError, TimeoutError, OSError):
        raise TokenExchangeError("Google authorization exchange failed") from None
    if len(payload) > 65536:
        raise TokenExchangeError("Google authorization response too large")
    try:
        data = json.loads(payload)
    except (ValueError, UnicodeError):
        raise TokenExchangeError("Invalid Google authorization response") from None
    if not isinstance(data, dict) or not all(
            isinstance(data.get(key), str) and data[key] for key in
            ("access_token", "refresh_token")):
        raise TokenExchangeError("Google did not return offline credentials")
    if data.get("token_type", "Bearer").lower() != "bearer":
        raise TokenExchangeError("Unexpected Google token type")
    try:
        expires = int(data.get("expires_in", 3600))
    except (TypeError, ValueError):
        raise TokenExchangeError("Invalid Google token expiration") from None
    if not 1 <= expires <= 86400:
        raise TokenExchangeError("Invalid Google token expiration")
    return {"access_token": data["access_token"],
            "refresh_token": data["refresh_token"],
            "expires_at": clock() + expires,
            "scope": str(data.get("scope", provider.scope)),
            "token_type": "Bearer"}
