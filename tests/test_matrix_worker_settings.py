"""Matrix worker settings precedence and safe disable tests."""
import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from universal_led import matrix_worker


class StopBeforeDriver(Exception):
    pass


class MatrixWorkerSettingsTests(unittest.TestCase):
    def test_legacy_service_arguments_work_without_config_file(self):
        with tempfile.TemporaryDirectory() as directory:
            config = Path(directory) / "missing.json"
            argv = ["matrix_worker", "--config-file", str(config),
                    "--mapping", "adafruit-hat", "--brightness", "40",
                    "--gpio-slowdown", "4"]
            with patch("sys.argv", argv), patch.object(matrix_worker, "create_matrix",
                side_effect=StopBeforeDriver) as create:
                with self.assertRaises(StopBeforeDriver):
                    matrix_worker.main()
                create.assert_called_once_with(gpio_mapping="adafruit-hat",
                                               brightness=40, gpio_slowdown=4)

    def test_saved_config_overrides_legacy_service_arguments(self):
        with tempfile.TemporaryDirectory() as directory:
            config = Path(directory) / "matrix.json"
            config.write_text(json.dumps({"brightness": 23, "gpio_slowdown": 3}))
            argv = ["matrix_worker", "--config-file", str(config),
                    "--brightness", "40", "--gpio-slowdown", "4"]
            with patch("sys.argv", argv), patch.object(matrix_worker, "create_matrix",
                side_effect=StopBeforeDriver) as create:
                with self.assertRaises(StopBeforeDriver):
                    matrix_worker.main()
                create.assert_called_once_with(gpio_mapping="adafruit-hat",
                                               brightness=23, gpio_slowdown=3)

    def test_disabled_config_never_opens_matrix_driver(self):
        with tempfile.TemporaryDirectory() as directory:
            config = Path(directory) / "matrix.json"
            config.write_text(json.dumps({"enabled": False}))
            with patch("sys.argv", ["matrix_worker", "--config-file", str(config)]), \
                 patch.object(matrix_worker, "create_matrix") as create:
                matrix_worker.main()
                create.assert_not_called()

    def test_invalid_config_fails_before_opening_driver(self):
        with tempfile.TemporaryDirectory() as directory:
            config = Path(directory) / "matrix.json"
            config.write_text(json.dumps({"brightness": 500}))
            with patch("sys.argv", ["matrix_worker", "--config-file", str(config)]), \
                 patch.object(matrix_worker, "create_matrix") as create:
                with self.assertRaises(SystemExit) as caught:
                    matrix_worker.main()
                self.assertEqual(caught.exception.code, 2)
                create.assert_not_called()


if __name__ == "__main__":
    unittest.main()
