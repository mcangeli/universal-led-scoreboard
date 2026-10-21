"""Provider policy regression tests."""
import unittest
from universal_led.plugin_oauth_providers import ProviderError, resolve_provider, public_provider_info


class ProviderPolicyTests(unittest.TestCase):
    def test_calendar_uses_readonly_google_scope(self):
        provider = resolve_provider("daily-calendar", "google-calendar")
        self.assertEqual(provider.scope, "https://www.googleapis.com/auth/calendar.readonly")
        self.assertEqual(provider.token_endpoint, "https://oauth2.googleapis.com/token")

    def test_other_plugins_cannot_claim_google_credentials(self):
        with self.assertRaises(ProviderError):
            resolve_provider("swimming-fish", "google-calendar")

    def test_arbitrary_provider_endpoint_not_accepted(self):
        with self.assertRaises(ProviderError):
            resolve_provider("daily-calendar", "https://attacker.example/collect")

    def test_public_metadata_excludes_token_endpoint(self):
        info = public_provider_info("daily-calendar", "google-calendar")
        self.assertNotIn("token_endpoint", info)


if __name__ == "__main__":
    unittest.main()
