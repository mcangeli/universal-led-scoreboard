"""HTTP security checks for local Google pairing initiation."""
import http.client
import json
import tempfile
import threading
import unittest
from http.server import ThreadingHTTPServer
from unittest.mock import patch

from universal_led.configurator import make_handler


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

    def request(self, *, cookie=None, csrf=None, payload=None):
        body = json.dumps(payload if payload is not None else
                          {"plugin_id": "daily-calendar", "provider": "google-calendar"})
        headers = {"Content-Type": "application/json"}
        if cookie is not None:
            headers["Cookie"] = "uls_session=" + cookie
        if csrf is not None:
            headers["X-Configurator-Token"] = csrf
        connection = http.client.HTTPConnection("127.0.0.1", self.server.server_port, timeout=5)
        try:
            connection.request("POST", "/api/plugins/oauth/pairing/start", body, headers)
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


if __name__ == "__main__":
    unittest.main()
