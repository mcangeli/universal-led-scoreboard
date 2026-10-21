"""Security regression tests for the Core plugin OAuth state manager."""
import unittest
from urllib.parse import parse_qs, urlsplit

from universal_led.plugin_oauth import OAuthError, PendingAuthorizations


class PluginOAuthTests(unittest.TestCase):
    def setUp(self):
        self.now = [100]
        self.manager = PendingAuthorizations(clock=lambda: self.now[0])
        self.args = dict(plugin_id="daily-calendar", session_id="admin-session",
                         client_id="google-client",
                         redirect_uri="https://board.example/api/plugins/oauth/callback",
                         authorization_endpoint="https://accounts.google.com/o/oauth2/v2/auth",
                         scope="https://www.googleapis.com/auth/calendar.readonly")

    def start(self):
        url = self.manager.begin(**self.args)
        return url, parse_qs(urlsplit(url).query)["state"][0]

    def test_pkce_scope_and_no_verifier_in_url(self):
        url, state = self.start()
        query = parse_qs(urlsplit(url).query)
        self.assertEqual(query["code_challenge_method"], ["S256"])
        self.assertEqual(query["scope"], [self.args["scope"]])
        self.assertNotIn("code_verifier", query)
        result = self.manager.consume(state=state, session_id="admin-session",
                                      plugin_id="daily-calendar", code="auth-code")
        self.assertGreaterEqual(len(result["code_verifier"]), 43)

    def test_replay_rejected(self):
        _, state = self.start()
        self.manager.consume(state=state, session_id="admin-session",
                             plugin_id="daily-calendar", code="auth-code")
        with self.assertRaises(OAuthError):
            self.manager.consume(state=state, session_id="admin-session",
                                 plugin_id="daily-calendar", code="auth-code")

    def test_wrong_session_consumes_state(self):
        _, state = self.start()
        with self.assertRaises(OAuthError):
            self.manager.consume(state=state, session_id="other",
                                 plugin_id="daily-calendar", code="auth-code")
        with self.assertRaises(OAuthError):
            self.manager.consume(state=state, session_id="admin-session",
                                 plugin_id="daily-calendar", code="auth-code")

    def test_expiration(self):
        _, state = self.start()
        self.now[0] = 701
        with self.assertRaises(OAuthError):
            self.manager.consume(state=state, session_id="admin-session",
                                 plugin_id="daily-calendar", code="auth-code")

    def test_reject_insecure_redirect(self):
        self.args["redirect_uri"] = "http://board.example/callback"
        with self.assertRaises(OAuthError):
            self.manager.begin(**self.args)


if __name__ == "__main__":
    unittest.main()
