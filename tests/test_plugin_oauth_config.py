import json
from pathlib import Path
import tempfile
import unittest

from universal_led.plugin_oauth_config import OAuthConfigError, load_google_client, google_connection_status
from universal_led.plugin_oauth_vault import PluginTokenVault


class OAuthConfigTests(unittest.TestCase):
    def test_https_redirect_derived_from_explicit_origin(self):
        with tempfile.TemporaryDirectory() as root:
            path = Path(root) / "google.json"
            path.write_text(json.dumps({"client_id": "example.apps.googleusercontent.com",
                                        "public_origin": "https://board.example"}))
            self.assertEqual(load_google_client(path)["redirect_uri"],
                             "https://board.example/api/plugins/oauth/callback")
            self.assertEqual(google_connection_status(path, PluginTokenVault(Path(root) / "vault"))["connected"], False)

    def test_reject_http_and_redirect_injection(self):
        with tempfile.TemporaryDirectory() as root:
            path = Path(root) / "google.json"
            for origin in ("http://board.example", "https://board.example/evil",
                           "https://board.example@attacker.example/callback",
                           "https://board.example?next=evil"):
                path.write_text(json.dumps({"client_id": "example.apps.googleusercontent.com",
                                            "public_origin": origin}))
                with self.assertRaises(OAuthConfigError):
                    load_google_client(path)

    def test_missing_configuration_is_not_connected(self):
        with tempfile.TemporaryDirectory() as root:
            self.assertEqual(google_connection_status(Path(root) / "missing",
                             PluginTokenVault(Path(root) / "vault")),
                             {"configured": False, "connected": False})


if __name__ == "__main__":
    unittest.main()
