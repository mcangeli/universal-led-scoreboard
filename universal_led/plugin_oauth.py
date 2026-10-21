"""Security boundaries for plugin OAuth authorization flows.

The configurator owns authentication and HTTP routes. This module validates
provider metadata, binds pending requests to an administrator session, and
provides single-use state validation. Never serialize pending requests to
portable configuration backups.
"""
from __future__ import annotations

import hashlib
import hmac
import secrets
import time
from urllib.parse import urlencode, urlsplit

MAX_PENDING = 32
STATE_TTL = 600


class OAuthError(ValueError):
    pass


def _https_uri(uri):
    if not isinstance(uri, str):
        raise OAuthError("Invalid redirect URI")
    parsed = urlsplit(uri)
    if (parsed.scheme != "https" or not parsed.hostname or
            parsed.username or parsed.password or parsed.fragment):
        raise OAuthError("Redirect URI must be HTTPS")
    return uri


class PendingAuthorizations:
    """In-memory, single-use authorization state scoped to admin sessions."""

    def __init__(self, clock=time.time):
        self._clock = clock
        self._pending = {}

    def begin(self, *, plugin_id, session_id, client_id, redirect_uri,
              authorization_endpoint, scope):
        if not all(isinstance(x, str) and x for x in
                   (plugin_id, session_id, client_id, scope)):
            raise OAuthError("Missing authorization configuration")
        redirect_uri = _https_uri(redirect_uri)
        endpoint = _https_uri(authorization_endpoint)
        if len(self._pending) >= MAX_PENDING:
            self._prune()
            if len(self._pending) >= MAX_PENDING:
                raise OAuthError("Too many pending authorizations")
        state = secrets.token_urlsafe(32)
        verifier = secrets.token_urlsafe(48)
        challenge = __import__("base64").urlsafe_b64encode(
            hashlib.sha256(verifier.encode("ascii")).digest()
        ).rstrip(b"=").decode("ascii")
        self._pending[state] = {
            "plugin_id": plugin_id, "session_id": session_id,
            "redirect_uri": redirect_uri, "verifier": verifier,
            "expires_at": self._clock() + STATE_TTL,
        }
        params = {"client_id": client_id, "redirect_uri": redirect_uri,
                  "response_type": "code", "scope": scope, "state": state,
                  "code_challenge": challenge, "code_challenge_method": "S256",
                  "access_type": "offline"}
        return endpoint + ("&" if "?" in endpoint else "?") + urlencode(params)

    def _prune(self):
        now = self._clock()
        for state, pending in list(self._pending.items()):
            if pending["expires_at"] <= now:
                del self._pending[state]

    def consume(self, *, state, session_id, plugin_id, code):
        if not isinstance(state, str) or not state:
            raise OAuthError("Invalid authorization state")
        # Remove first: even a failed callback cannot be replayed.
        pending = self._pending.pop(state, None)
        if not pending or pending["expires_at"] <= self._clock():
            raise OAuthError("Authorization expired or already used")
        if not (isinstance(session_id, str) and isinstance(plugin_id, str) and
                hmac.compare_digest(pending["session_id"], session_id) and
                hmac.compare_digest(pending["plugin_id"], plugin_id)):
            raise OAuthError("Authorization session mismatch")
        if not isinstance(code, str) or not code.strip():
            raise OAuthError("Authorization code missing")
        return {"code": code, "code_verifier": pending["verifier"],
                "redirect_uri": pending["redirect_uri"]}
