"""Encrypt a one-time local pairing payload to the scoreboard's ephemeral key.

The pairing key is created on the Pi and never exported. The desktop helper
encrypts to its public key; the Pi decrypts and validates a one-use ticket.
This module does not itself authenticate the Pi to the desktop client:
the helper must verify the public-key fingerprint out of band.
"""
from __future__ import annotations

import base64
import json
import secrets
import time

try:
    from cryptography.exceptions import InvalidTag
    from cryptography.hazmat.primitives import hashes, serialization
    from cryptography.hazmat.primitives.asymmetric import padding, rsa
    from cryptography.hazmat.primitives.ciphers.aead import AESGCM
except ImportError:
    AESGCM = None
    InvalidTag = None

MAX_ENVELOPE = 16384
KEY_TTL = 300


class PairingCryptoError(ValueError):
    pass


def _require_crypto():
    if AESGCM is None:
        raise PairingCryptoError("cryptography package required for secure pairing")


def _b64(data):
    return base64.urlsafe_b64encode(data).decode("ascii").rstrip("=")


def _unb64(value):
    if not isinstance(value, str) or len(value) > MAX_ENVELOPE:
        raise PairingCryptoError("Invalid pairing envelope")
    try:
        return base64.b64decode(value + "=" * (-len(value) % 4), altchars=b"-_", validate=True)
    except (ValueError, base64.binascii.Error):
        raise PairingCryptoError("Invalid pairing envelope") from None


class PairingKey:
    def __init__(self, clock=time.time):
        _require_crypto()
        self._clock = clock
        self._created = clock()
        self._private = rsa.generate_private_key(public_exponent=65537, key_size=2048)

    def public_pem(self):
        return self._private.public_key().public_bytes(
            serialization.Encoding.PEM, serialization.PublicFormat.SubjectPublicKeyInfo
        ).decode("ascii")

    def fingerprint(self):
        digest = hashes.Hash(hashes.SHA256())
        digest.update(self.public_pem().encode("ascii"))
        return digest.finalize().hex()

    def decrypt(self, envelope):
        if self._clock() - self._created >= KEY_TTL:
            raise PairingCryptoError("Pairing key expired")
        if not isinstance(envelope, dict) or set(envelope) != {"key", "nonce", "ciphertext"}:
            raise PairingCryptoError("Invalid pairing envelope")
        try:
            symmetric = self._private.decrypt(
                _unb64(envelope["key"]),
                padding.OAEP(mgf=padding.MGF1(algorithm=hashes.SHA256()),
                             algorithm=hashes.SHA256(), label=None))
            if len(symmetric) != 32:
                raise PairingCryptoError("Invalid pairing key")
            plaintext = AESGCM(symmetric).decrypt(
                _unb64(envelope["nonce"]), _unb64(envelope["ciphertext"]), None)
            if len(plaintext) > 8192:
                raise PairingCryptoError("Pairing payload too large")
            result = json.loads(plaintext)
            if not isinstance(result, dict):
                raise PairingCryptoError("Invalid pairing payload")
            return result
        except (ValueError, TypeError, KeyError, InvalidTag):
            raise PairingCryptoError("Unable to decrypt pairing payload") from None


def encrypt_for_public_key(public_pem, payload):
    _require_crypto()
    if not isinstance(payload, dict):
        raise PairingCryptoError("Invalid pairing payload")
    plaintext = json.dumps(payload, separators=(",", ":")).encode("utf-8")
    if len(plaintext) > 8192:
        raise PairingCryptoError("Pairing payload too large")
    public = serialization.load_pem_public_key(public_pem.encode("ascii"))
    if not isinstance(public, rsa.RSAPublicKey) or public.key_size < 2048:
        raise PairingCryptoError("Invalid pairing public key")
    symmetric = secrets.token_bytes(32)
    nonce = secrets.token_bytes(12)
    return {
        "key": _b64(public.encrypt(
            symmetric, padding.OAEP(mgf=padding.MGF1(algorithm=hashes.SHA256()),
                                    algorithm=hashes.SHA256(), label=None))),
        "nonce": _b64(nonce),
        "ciphertext": _b64(AESGCM(symmetric).encrypt(nonce, plaintext, None)),
    }
