import unittest
from universal_led.plugin_oauth_pairing_coordinator import PairingCoordinator
from universal_led.plugin_oauth_pairing_crypto import encrypt_for_public_key
from universal_led.plugin_oauth_pairing import PairingError


class CoordinatorTests(unittest.TestCase):
    def test_receive_once(self):
        coordinator = PairingCoordinator()
        issued = coordinator.begin(plugin_id="daily-calendar", provider_id="google-calendar", session_id="admin")
        envelope = encrypt_for_public_key(issued["public_key"], {"refresh_token": "private"})
        args = dict(ticket=issued["ticket"], plugin_id="daily-calendar",
                    provider_id="google-calendar", session_id="admin", envelope=envelope)
        self.assertEqual(coordinator.receive(**args)["refresh_token"], "private")
        with self.assertRaises(PairingError):
            coordinator.receive(**args)

    def test_wrong_session_consumes(self):
        coordinator = PairingCoordinator()
        issued = coordinator.begin(plugin_id="daily-calendar", provider_id="google-calendar", session_id="admin")
        envelope = encrypt_for_public_key(issued["public_key"], {"refresh_token": "private"})
        args = dict(ticket=issued["ticket"], plugin_id="daily-calendar",
                    provider_id="google-calendar", session_id="wrong", envelope=envelope)
        with self.assertRaises(PairingError):
            coordinator.receive(**args)
        args["session_id"] = "admin"
        with self.assertRaises(PairingError):
            coordinator.receive(**args)

    def test_invalid_payload_consumes(self):
        coordinator = PairingCoordinator()
        issued = coordinator.begin(plugin_id="daily-calendar", provider_id="google-calendar", session_id="admin")
        args = dict(ticket=issued["ticket"], plugin_id="daily-calendar",
                    provider_id="google-calendar", session_id="admin",
                    envelope=encrypt_for_public_key(issued["public_key"], {"wrong": "data"}))
        with self.assertRaises(PairingError):
            coordinator.receive(**args)
        with self.assertRaises(PairingError):
            coordinator.receive(**args)


if __name__ == "__main__":
    unittest.main()
