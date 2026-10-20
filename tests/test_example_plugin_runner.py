"""Opt-in Hello World execution diagnostic regression tests."""
import tempfile
import unittest
from pathlib import Path

from universal_led.example_plugin_runner import render_hello_world, main
from universal_led.frame_bridge import read_frame


class ExamplePluginRunnerTests(unittest.TestCase):
    def test_renders_expected_frame(self):
        frame = render_hello_world()
        self.assertEqual((frame.width, frame.height), (64, 32))
        self.assertTrue(any(channel for row in frame.pixels for pixel in row for channel in pixel))

    def test_explicit_output_round_trip(self):
        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory) / "hello.ppm"
            main(["--output", str(output)])
            self.assertEqual(read_frame(output).ppm(), render_hello_world().ppm())


if __name__ == "__main__":
    unittest.main()
