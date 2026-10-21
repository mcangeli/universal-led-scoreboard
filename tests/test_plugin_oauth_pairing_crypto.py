import unittest

from universal_led.plugin_oauth_pairing_crypto import (
    AESGCM, PairingCryptoError, PairingKey, encrypt_for_public_key,
)


@unittest.skipUnless(AESGCM is not None, 'optional cryptography dependency unavailable')
class PairingCryptoTests(unittest.TestCase):
    def test_encrypted_roundtrip(self):
        key = PairingKey()
        data = {"ticket": "one-use", "refresh_token": "secret"}
        envelope = encrypt_for_public_key(key.public_pem(), data)
        self.assertNotIn("secret", str(envelope))
        self.assertEqual(key.decrypt(envelope), data)
        self.assertEqual(len(key.fingerprint()), 64)

    def test_tampering_rejected(self):
        key = PairingKey()
        envelope = encrypt_for_public_key(key.public_pem(), {"ticket": "one-use"})
        envelope["ciphertext"] = "AAAA"
        with self.assertRaises(PairingCryptoError):
            key.decrypt(envelope)

    def test_wrong_key_rejected(self):
        first = PairingKey()
        second = PairingKey()
        envelope = encrypt_for_public_key(first.public_pem(), {"ticket": "one-use"})
        with self.assertRaises(PairingCryptoError):
            second.decrypt(envelope)

    def test_expired_key_rejected(self):
        now = [100]
        key = PairingKey(clock=lambda: now[0])
        envelope = encrypt_for_public_key(key.public_pem(), {"ticket": "one-use"})
        now[0] += 301
        with self.assertRaises(PairingCryptoError):
            key.decrypt(envelope)


if __name__ == "__main__":
    unittest.main()
