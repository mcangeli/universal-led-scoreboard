import tempfile
import unittest
from universal_led.auth import set_password,verify_password,Sessions
from universal_led.configurator import HTML,LOGIN_HTML

class Preview19Tests(unittest.TestCase):
    def test_password_storage_and_verification(self):
        with tempfile.TemporaryDirectory() as directory:
            set_password(directory,'test-password-123')
            self.assertTrue(verify_password(directory,'test-password-123'))
            self.assertFalse(verify_password(directory,'incorrect'))
    def test_short_password_rejected(self):
        with tempfile.TemporaryDirectory() as directory:
            with self.assertRaises(ValueError):
                set_password(directory,'short')
    def test_sessions(self):
        sessions=Sessions()
        token=sessions.create()
        self.assertTrue(sessions.valid(token))
        sessions.revoke(token)
        self.assertFalse(sessions.valid(token))
    def test_login_and_logout_ui(self):
        self.assertIn('action="/login"',LOGIN_HTML)
        self.assertIn('logout()',HTML)
if __name__=='__main__':
    unittest.main()
