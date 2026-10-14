import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch
from universal_led.auth import Sessions,set_password

class PersistentSessionTests(unittest.TestCase):
    def test_restart_preserves_session(self):
        with tempfile.TemporaryDirectory() as directory:
            set_password(directory,'example-password-123')
            token=Sessions(directory).create()
            self.assertTrue(Sessions(directory).valid(token))
            self.assertNotIn(token,(Path(directory)/'sessions.sqlite3').read_bytes().decode('latin1'))
            Sessions(directory).revoke(token)
            self.assertFalse(Sessions(directory).valid(token))
    def test_password_reset_invalidates_sessions(self):
        with tempfile.TemporaryDirectory() as directory:
            set_password(directory,'example-password-123')
            token=Sessions(directory).create()
            set_password(directory,'another-password-123')
            self.assertFalse(Sessions(directory).valid(token))
    def test_expired_session_is_rejected(self):
        with tempfile.TemporaryDirectory() as directory:
            set_password(directory,'example-password-123')
            with patch('universal_led.auth.time.time',return_value=100):
                token=Sessions(directory).create()
            with patch('universal_led.auth.time.time',return_value=100+8*3600+1):
                self.assertFalse(Sessions(directory).valid(token))

if __name__=='__main__':
    unittest.main()
