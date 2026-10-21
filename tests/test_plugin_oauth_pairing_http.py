"""HTTP security checks for local Google pairing initiation."""
import http.client
import json
import tempfile
import threading
import unittest
from http.server import ThreadingHTTPServer
from unittest.mock import patch

from universal_led.configurator import make_handler
from universal_led.plugin_oauth_pairing_crypto import encrypt_for_public_key


class PairingHttpTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.auth = patch("universal_led.configurator.Sessions.valid",
                          lambda _sessions, cookie: cookie == "valid-session")
        self.registry = patch("universal_led.plugin_registry.read_registry",
                              return_value={"daily-calendar": {}})
        self.auth.start()
        self.registry.start()
        self.addCleanup(self.auth.stop)
        self.addCleanup(self.registry.stop)
        handler = make_handler(self.tmp.name, "csrf-secret")
        self.server = ThreadingHTTPServer(("127.0.0.1", 0), handler)
        self.thread = threading.Thread(target=self.server.serve_forever, daemon=True)
        self.thread.start()
        self.addCleanup(self.server.server_close)
        self.addCleanup(self.server.shutdown)
        self.addCleanup(self.thread.join, 3)

    def request(self, *, cookie=None, csrf=None, payload=None, endpoint="/api/plugins/oauth/pairing/start"):
        body = json.dumps(payload if payload is not None else
                          {"plugin_id": "daily-calendar", "provider": "google-calendar"})
        headers = {"Content-Type": "application/json"}
        if cookie is not None:
            headers["Cookie"] = "uls_session=" + cookie
        if csrf is not None:
            headers["X-Configurator-Token"] = csrf
        connection = http.client.HTTPConnection("127.0.0.1", self.server.server_port, timeout=5)
        try:
            connection.request("POST", endpoint, body, headers)
            response = connection.getresponse()
            return response.status, json.loads(response.read())
        finally:
            connection.close()

    def test_anonymous_denied(self):
        status, _ = self.request(csrf="csrf-secret")
        self.assertEqual(status, 401)

    def test_csrf_required(self):
        status, _ = self.request(cookie="valid-session")
        self.assertEqual(status, 403)

    def test_authenticated_admin_receives_ephemeral_key(self):
        status, body = self.request(cookie="valid-session", csrf="csrf-secret")
        self.assertEqual(status, 200)
        self.assertIn("BEGIN PUBLIC KEY", body["public_key"])
        self.assertTrue(body["ticket"])
        self.assertTrue(body["fingerprint"])
        self.assertEqual(body["expires_in"], 300)
        self.assertNotIn("private_key", body)

    def test_other_plugin_rejected(self):
        status, _ = self.request(cookie="valid-session", csrf="csrf-secret",
                                 payload={"plugin_id": "swimming-fish",
                                          "provider": "google-calendar"})
        self.assertEqual(status, 400)


    def test_import_requires_authentication_and_csrf(self):
        payload={"plugin_id":"daily-calendar","provider":"google-calendar",
                 "ticket":"bogus","envelope":{}}
        endpoint="/api/plugins/oauth/pairing/import"
        self.assertEqual(self.request(csrf="csrf-secret",payload=payload,endpoint=endpoint)[0],401)
        self.assertEqual(self.request(cookie="valid-session",payload=payload,endpoint=endpoint)[0],403)

    def test_invalid_ticket_cannot_import(self):
        status, _ = self.request(cookie="valid-session",csrf="csrf-secret",
            payload={"plugin_id":"daily-calendar","provider":"google-calendar",
                     "ticket":"bogus","envelope":{}},
            endpoint="/api/plugins/oauth/pairing/import")
        self.assertEqual(status,400)

    def test_valid_encrypted_import_uses_private_vault(self):
        status, issued = self.request(cookie="valid-session",csrf="csrf-secret")
        self.assertEqual(status,200)
        envelope=encrypt_for_public_key(issued["public_key"], {
            "access_token":"access","refresh_token":"refresh",
            "client_id":"desktop.apps.googleusercontent.com","expires_at":2000000000})
        payload={"plugin_id":"daily-calendar","provider":"google-calendar",
                 "ticket":issued["ticket"],"envelope":envelope}
        endpoint="/api/plugins/oauth/pairing/import"
        with patch("universal_led.plugin_oauth_vault.PluginTokenVault.save") as save:
            status, response=self.request(cookie="valid-session",csrf="csrf-secret",
                                         payload=payload,endpoint=endpoint)
            self.assertEqual(status,200,response)
            self.assertEqual(response,{"connected":True})
            save.assert_called_once()
            self.assertEqual(save.call_args.args[0],"daily-calendar")
            self.assertEqual(save.call_args.args[1]["refresh_token"],"refresh")
            self.assertEqual(self.request(cookie="valid-session",csrf="csrf-secret",
                                          payload=payload,endpoint=endpoint)[0],400)


if __name__ == "__main__":
    unittest.main()
