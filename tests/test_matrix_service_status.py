"""Matrix service status presentation tests."""
import unittest

from universal_led.matrix_settings import matrix_service_label


class MatrixServiceStatusTests(unittest.TestCase):
    def test_running_when_enabled(self):
        self.assertEqual(matrix_service_label("active", True), "Running")

    def test_disabled_is_not_reported_as_failure(self):
        self.assertEqual(matrix_service_label("inactive", False), "Disabled by configuration")

    def test_unapplied_disable_is_visible(self):
        self.assertIn("not yet applied", matrix_service_label("active", False))

    def test_enabled_but_failed_is_actionable(self):
        self.assertIn("check service", matrix_service_label("failed", True))

    def test_unexpected_state_remains_visible(self):
        self.assertEqual(matrix_service_label("activating", True), "Service state: activating")


if __name__ == "__main__":
    unittest.main()
