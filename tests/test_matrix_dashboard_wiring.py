"""Regression guards for the matrix settings dashboard wiring."""
import unittest

from universal_led.configurator import HTML, make_handler


class MatrixDashboardWiringTests(unittest.TestCase):
    def test_matrix_page_has_separate_save_and_apply(self):
        self.assertIn('data-page="matrix-settings"', HTML)
        self.assertIn('onclick="saveMatrixSettings()"', HTML)
        self.assertIn('onclick="applyMatrixSettings()"', HTML)

    def test_matrix_page_reports_service_status(self):
        self.assertIn('id="matrix-service-state"', HTML)
        self.assertIn("'/api/matrix-status'", HTML)

    def test_apply_requires_explicit_confirmation(self):
        self.assertIn("JSON.stringify({confirm:true})", HTML)
        self.assertIn("if(!confirm(", HTML)


if __name__ == "__main__":
    unittest.main()
