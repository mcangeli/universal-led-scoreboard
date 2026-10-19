"""Portable restore remains transactional when a later section fails."""
import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from universal_led.config_archive import export_portable, restore_portable


class PortableRestoreFailureTests(unittest.TestCase):
    def test_failed_second_replace_rolls_back_first_and_preserves_matrix(self):
        with tempfile.TemporaryDirectory() as source, tempfile.TemporaryDirectory() as destination:
            src, dst = Path(source), Path(destination)
            (src / "teams.json").write_text(json.dumps({"ATL": {"primary": "#123456"}}))
            (src / "scoreboard.json").write_text(json.dumps({"background": "#112233"}))
            (dst / "teams.json").write_text('{"ATL":{"primary":"#654321"}}')
            (dst / "scoreboard.json").write_text('{"background":"#334455"}')
            (dst / "matrix.json").write_text('{"enabled":true}')
            original = {name: (dst / name).read_bytes() for name in
                        ("teams.json", "scoreboard.json", "matrix.json")}
            payload = export_portable(src)
            import universal_led.config_archive as archive_module
            import os
            actual_replace = os.replace
            calls = []

            def fail_second_replace(src_path, dst_path):
                calls.append(str(dst_path))
                if len(calls) == 2:
                    raise OSError("simulated second section write failure")
                return actual_replace(src_path, dst_path)

            with patch.object(archive_module.os, "replace", side_effect=fail_second_replace):
                with self.assertRaisesRegex(OSError, "simulated"):
                    restore_portable(payload, dst, ["teams", "scoreboard"])
            for name, before in original.items():
                self.assertEqual((dst / name).read_bytes(), before, name)

    def test_rejects_unselected_or_device_specific_sections_without_writes(self):
        with tempfile.TemporaryDirectory() as source, tempfile.TemporaryDirectory() as destination:
            src, dst = Path(source), Path(destination)
            (src / "teams.json").write_text('{}')
            (dst / "matrix.json").write_text('{"enabled":true}')
            payload = export_portable(src)
            with self.assertRaises(ValueError):
                restore_portable(payload, dst, ["matrix"])
            self.assertEqual((dst / "matrix.json").read_text(), '{"enabled":true}')
            self.assertFalse((dst / "teams.json").exists())


if __name__ == "__main__":
    unittest.main()
