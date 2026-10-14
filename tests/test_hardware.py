import tempfile
import unittest
from pathlib import Path
from universal_led.hardware import detect_model, detect_os, HardwareInfo, physical_driver_warning

class HardwareTests(unittest.TestCase):
    def test_model_reading(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / 'model'
            path.write_bytes(b'Raspberry Pi 5 Model B Rev 1.0\x00')
            self.assertEqual(detect_model(str(path)), 'Raspberry Pi 5 Model B Rev 1.0')
    def test_missing_model(self):
        self.assertEqual(detect_model('/nonexistent/universal-led-model'), 'Unknown hardware')
    def test_os_release(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / 'os-release'
            path.write_text('NAME="Raspberry Pi OS"\nVERSION_CODENAME=trixie\n')
            self.assertEqual(detect_os(str(path)), ('Raspberry Pi OS', 'trixie'))
    def test_pi5_warning(self):
        warning = physical_driver_warning(HardwareInfo('Raspberry Pi 5 Model B', 'Raspberry Pi OS', 'trixie'))
        self.assertIn('Pi 5', warning)

if __name__ == '__main__':
    unittest.main()
