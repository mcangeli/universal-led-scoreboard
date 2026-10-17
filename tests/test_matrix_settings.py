import json
import tempfile
import unittest
from pathlib import Path

from universal_led.matrix_settings import DEFAULTS, load_matrix_settings, validate_matrix_settings


class MatrixSettingsTests(unittest.TestCase):
    def test_defaults_preserve_working_pi(self):
        self.assertEqual(DEFAULTS["mapping"], "adafruit-hat")
        self.assertEqual(DEFAULTS["brightness"], 40)
        self.assertEqual(DEFAULTS["gpio_slowdown"], 4)
        self.assertTrue(DEFAULTS["enabled"])

    def test_missing_file_uses_defaults(self):
        with tempfile.TemporaryDirectory() as directory:
            self.assertEqual(load_matrix_settings(Path(directory) / "matrix.json"), DEFAULTS)

    def test_partial_file_merges_defaults(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "matrix.json"
            path.write_text(json.dumps({"brightness": 25}))
            self.assertEqual(load_matrix_settings(path)["gpio_slowdown"], 4)
            self.assertEqual(load_matrix_settings(path)["brightness"], 25)

    def test_valid_disable(self):
        self.assertFalse(validate_matrix_settings({"enabled": False})["enabled"])

    def test_reject_unknown_keys(self):
        with self.assertRaises(ValueError):
            validate_matrix_settings({"unexpected": True})

    def test_reject_invalid_brightness(self):
        for value in (0, 101, True, "40"):
            with self.subTest(value=value), self.assertRaises(ValueError):
                validate_matrix_settings({"brightness": value})

    def test_reject_invalid_slowdown(self):
        for value in (-1, 11, 2.5):
            with self.subTest(value=value), self.assertRaises(ValueError):
                validate_matrix_settings({"gpio_slowdown": value})

    def test_reject_unsupported_mapping(self):
        with self.assertRaises(ValueError):
            validate_matrix_settings({"mapping": "arbitrary"})

    def test_reject_invalid_interval(self):
        for value in (0, 11, True, "0.2"):
            with self.subTest(value=value), self.assertRaises(ValueError):
                validate_matrix_settings({"interval": value})


if __name__ == "__main__":
    unittest.main()
