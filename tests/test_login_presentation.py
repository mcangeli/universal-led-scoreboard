"""Browser login should be human-readable; protected APIs remain JSON."""
import unittest

from universal_led.configurator import LOGIN_HTML
from universal_led import configurator
import inspect


class LoginPresentationTests(unittest.TestCase):
    def test_login_has_error_placeholder_and_accessible_alert(self):
        self.assertIn("__LOGIN_ERROR__", LOGIN_HTML)
        self.assertIn('role="alert"', inspect.getsource(configurator))
        self.assertIn('Incorrect password. Please try again.', inspect.getsource(configurator))

    def test_login_form_stays_password_only(self):
        self.assertIn('type="password"', LOGIN_HTML)
        self.assertIn('autocomplete="current-password"', LOGIN_HTML)
        self.assertIn('method="post"', LOGIN_HTML)

    def test_browser_redirect_and_api_401_remain_separate(self):
        source = inspect.getsource(configurator)
        self.assertIn("elif path.startswith('/api/'):", source)
        self.assertIn("self.send_json(401,{'error':'Authentication required'})", source)
        self.assertIn("self.send_header('Location','/login')", source)


if __name__ == "__main__":
    unittest.main()
