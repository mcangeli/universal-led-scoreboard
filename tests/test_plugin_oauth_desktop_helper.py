"""Desktop Google Calendar pairing helper security regressions."""
import importlib.util
import json
from pathlib import Path
import unittest

from universal_led.plugin_oauth_pairing_crypto import PairingKey

SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "uls-google-calendar-desktop.py"
spec = importlib.util.spec_from_file_location("uls_google_calendar_desktop", SCRIPT)
helper = importlib.util.module_from_spec(spec)
spec.loader.exec_module(helper)


class DesktopHelperTests(unittest.TestCase):
    def setUp(self):
        self.key = PairingKey()
        self.pairing = {"ticket": "a" * 44, "public_key": self.key.public_pem(),
                        "fingerprint": self.key.fingerprint(), "expires_in": 300}
        self.credentials = {"access_token": "access", "refresh_token": "refresh",
                            "client_id": "desktop.apps.googleusercontent.com",
                            "expires_at": 2000000000}

    def test_valid_fingerprint(self):
        self.assertEqual(helper.validate_pairing(self.pairing), self.key.fingerprint())

    def test_modified_public_key_rejected(self):
        altered = dict(self.pairing)
        altered["public_key"] = PairingKey().public_pem()
        with self.assertRaises(ValueError):
            helper.validate_pairing(altered)

    def test_malformed_ticket_rejected(self):
        altered = dict(self.pairing, ticket="short")
        with self.assertRaises(ValueError):
            helper.validate_pairing(altered)

    def test_encrypted_transfer_never_contains_plaintext_tokens(self):
        transfer = helper.build_transfer(self.pairing, self.credentials)
        wire = json.dumps(transfer)
        self.assertNotIn("refresh", wire)
        self.assertNotIn("access", wire)
        self.assertEqual(transfer["plugin_id"], "daily-calendar")
        self.assertEqual(self.key.decrypt(transfer["envelope"]), self.credentials)

    def test_reject_invalid_google_client_id(self):
        with self.assertRaises(ValueError):
            helper.authorize("not-a-desktop-client")


if __name__ == "__main__":
    unittest.main()
