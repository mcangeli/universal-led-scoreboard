"""One-time, short-lived authorization tickets for local desktop pairing.

A ticket is not an OAuth token. The eventual upload endpoint must also
provide an authenticated, confidential transport before accepting secrets.
"""
from __future__ import annotations

import hashlib
import hmac
import secrets
import time

PAIRING_TTL = 300
MAX_TICKETS = 16


class PairingError(ValueError):
    pass


class PairingTickets:
    def __init__(self, clock=time.time):
        self._clock = clock
        self._tickets = {}

    def _prune(self):
        now = self._clock()
        for digest, record in list(self._tickets.items()):
            if record["expires_at"] <= now:
                del self._tickets[digest]

    def issue(self, *, plugin_id, provider_id, session_id):
        if not all(isinstance(value, str) and value for value in
                   (plugin_id, provider_id, session_id)):
            raise PairingError("Missing pairing identity")
        from .plugin_oauth_providers import resolve_provider
        resolve_provider(plugin_id, provider_id)
        self._prune()
        if len(self._tickets) >= MAX_TICKETS:
            raise PairingError("Too many pending pairings")
        ticket = secrets.token_urlsafe(32)
        digest = hashlib.sha256(ticket.encode("ascii")).hexdigest()
        self._tickets[digest] = {
            "plugin_id": plugin_id,
            "provider_id": provider_id,
            "session_hash": hashlib.sha256(session_id.encode()).digest(),
            "expires_at": self._clock() + PAIRING_TTL,
        }
        return ticket

    def consume(self, *, ticket, plugin_id, provider_id, session_id):
        if not isinstance(ticket, str) or not ticket:
            raise PairingError("Invalid pairing ticket")
        digest = hashlib.sha256(ticket.encode()).hexdigest()
        record = self._tickets.pop(digest, None)
        if record is None or record["expires_at"] <= self._clock():
            raise PairingError("Pairing expired or already used")
        expected = hashlib.sha256(session_id.encode()).digest() if isinstance(session_id, str) else b""
        if not (hmac.compare_digest(record["session_hash"], expected)
                and record["plugin_id"] == plugin_id
                and record["provider_id"] == provider_id):
            raise PairingError("Pairing identity mismatch")
        return True
