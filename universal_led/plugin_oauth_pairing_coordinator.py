"""Session-scoped pairing coordinator; no HTTP or credential persistence.

Each pairing owns its own ephemeral key. A ticket cannot be reused with
another key, session, plugin or provider. The public key is for the desktop
helper; its fingerprint must be verified out of band before sending secrets.
"""
from __future__ import annotations

import time
import threading
from .plugin_oauth_pairing import PairingTickets, PairingError
from .plugin_oauth_pairing_crypto import PairingKey, PairingCryptoError


class PairingCoordinator:
    def __init__(self, clock=time.time):
        self._clock = clock
        self._lock = threading.RLock()
        self._tickets = PairingTickets(clock=clock)
        self._keys = {}

    def begin(self, *, plugin_id, provider_id, session_id):
        with self._lock:
            self._prune()
            ticket = self._tickets.issue(plugin_id=plugin_id,
                                         provider_id=provider_id,
                                         session_id=session_id)
            key = PairingKey(clock=self._clock)
            self._keys[ticket] = (key, self._clock() + 300)
            return {"ticket": ticket, "public_key": key.public_pem(),
                    "fingerprint": key.fingerprint(), "expires_in": 300}

    def _prune(self):
        now = self._clock()
        for ticket, (_, expires_at) in list(self._keys.items()):
            if expires_at <= now:
                del self._keys[ticket]

    def receive(self, *, ticket, plugin_id, provider_id, session_id, envelope):
        with self._lock:
            self._prune()
            entry = self._keys.pop(ticket, None) if isinstance(ticket, str) else None
            # Consume ticket before decrypting, including invalid encrypted requests.
            self._tickets.consume(ticket=ticket, plugin_id=plugin_id,
                                  provider_id=provider_id, session_id=session_id)
        if entry is None:
            raise PairingError("Pairing key expired or already used")
        payload = entry[0].decrypt(envelope)
        if not isinstance(payload.get("refresh_token"), str) or not payload["refresh_token"]:
            raise PairingError("Missing refresh token")
        return payload
