import unittest

from universal_led.wifi_connection_request import WifiRequest, validate_request


class WifiConnectionRequestTests(unittest.TestCase):
    def test_valid_prepare(self):
        request = validate_request({
            'action': 'prepare', 'interface': 'wlan0',
            'previous_connection': 'netplan-wlan0-home',
            'target_ssid': 'Guest Network',
        })
        self.assertIsInstance(request, WifiRequest)
        self.assertEqual(request.target_ssid, 'Guest Network')

    def test_valid_confirm(self):
        request = validate_request({'action': 'confirm', 'token': 'a' * 32})
        self.assertEqual(request.token, 'a' * 32)

    def test_valid_inspect(self):
        request = validate_request({'action': 'inspect', 'token': 'b' * 32})
        self.assertEqual(request.action, 'inspect')

    def test_rejects_unknown_action(self):
        with self.assertRaises(ValueError):
            validate_request({'action': 'execute', 'token': 'a' * 32})

    def test_rejects_unknown_fields(self):
        with self.assertRaises(ValueError):
            validate_request({'action': 'confirm', 'token': 'a' * 32,
                              'command': 'anything'})

    def test_rejects_password_field(self):
        with self.assertRaises(ValueError):
            validate_request({'action': 'prepare', 'interface': 'wlan0',
                              'previous_connection': 'Home',
                              'target_ssid': 'Guest', 'password': 'secret'})

    def test_rejects_bad_interface(self):
        with self.assertRaises(ValueError):
            validate_request({'action': 'prepare', 'interface': 'eth0',
                              'previous_connection': 'Home',
                              'target_ssid': 'Guest'})

    def test_rejects_control_characters_in_ssid(self):
        with self.assertRaises(ValueError):
            validate_request({'action': 'prepare', 'interface': 'wlan0',
                              'previous_connection': 'Home',
                              'target_ssid': 'Guest\nInjected'})

    def test_rejects_invalid_token(self):
        with self.assertRaises(ValueError):
            validate_request({'action': 'confirm', 'token': '../bad'})

    def test_rejects_extra_prepare_fields(self):
        with self.assertRaises(ValueError):
            validate_request({'action': 'prepare', 'interface': 'wlan0',
                              'previous_connection': 'Home',
                              'target_ssid': 'Guest', 'token': 'a' * 32})

    def test_rejects_non_object(self):
        with self.assertRaises(ValueError):
            validate_request(['confirm'])

    def test_rejects_overlong_ssid(self):
        with self.assertRaises(ValueError):
            validate_request({'action': 'prepare', 'interface': 'wlan0',
                              'previous_connection': 'Home',
                              'target_ssid': 'x' * 33})


if __name__ == '__main__':
    unittest.main()
