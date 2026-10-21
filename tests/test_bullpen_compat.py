"""Metadata-only Bullpen compatibility detection tests."""
import tempfile
import unittest
from pathlib import Path
from universal_led.bullpen_compat import detect_bullpen_package


class BullpenDetectionTests(unittest.TestCase):
    def test_pyproject_entry_point(self):
        with tempfile.TemporaryDirectory() as directory:
            (Path(directory) / "pyproject.toml").write_text(
                '[project.entry-points."bullpen.mlbled.plugin"]\nmagic_number = "magic_number:load"\n')
            result = detect_bullpen_package(directory)
            self.assertEqual([(x.name, x.entry_point) for x in result],
                             [("magic_number", "magic_number:load")])

    def test_setup_cfg_entry_point(self):
        with tempfile.TemporaryDirectory() as directory:
            (Path(directory) / "setup.cfg").write_text(
                "[options.entry_points]\nbullpen.mlbled.plugin =\n    monster = monster.plugin:load\n")
            self.assertEqual(detect_bullpen_package(directory)[0].name, "monster")

    def test_invalid_entry_point_not_loaded(self):
        with tempfile.TemporaryDirectory() as directory:
            (Path(directory) / "pyproject.toml").write_text(
                '[project.entry-points."bullpen.mlbled.plugin"]\nunsafe = "os:system()"\n')
            self.assertFalse(detect_bullpen_package(directory))

    def test_setup_py_not_executed(self):
        with tempfile.TemporaryDirectory() as directory:
            (Path(directory) / "setup.py").write_text("raise RuntimeError('must never run')")
            self.assertFalse(detect_bullpen_package(directory))


if __name__ == "__main__":
    unittest.main()
