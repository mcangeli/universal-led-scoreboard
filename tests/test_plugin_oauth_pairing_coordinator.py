import unittest
from concurrent.futures import ThreadPoolExecutor
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


    def test_concurrent_replay_only_one_succeeds(self):
        coordinator = PairingCoordinator()
        issued = coordinator.begin(plugin_id="daily-calendar", provider_id="google-calendar", session_id="admin")
        envelope = encrypt_for_public_key(issued["public_key"], {"refresh_token": "private"})
        args = dict(ticket=issued["ticket"], plugin_id="daily-calendar",
                    provider_id="google-calendar", session_id="admin", envelope=envelope)

        def attempt(_):
            try:
                coordinator.receive(**args)
                return True
            except PairingError:
                return False

        with ThreadPoolExecutor(max_workers=8) as pool:
            results = list(pool.map(attempt, range(24)))
        self.assertEqual(results.count(True), 1)
        self.assertEqual(results.count(False), 23)


if __name__ == "__main__":
    unittest.main()
