"""Tests for the documented native Hello World plugin example."""
import importlib.util
import json
import unittest
from pathlib import Path

from universal_led.display import Framebuffer
from universal_led.plugin_manifest import parse_manifest, discover_plugins


ROOT = Path(__file__).resolve().parents[1]
EXAMPLE = ROOT / "plugins" / "hello-world"


class HelloWorldPluginTests(unittest.TestCase):
    def test_manifest_is_valid(self):
        manifest = parse_manifest(json.loads((EXAMPLE / "uls-plugin.json").read_text()))
        self.assertEqual(manifest.plugin_id, "hello-world")
        self.assertEqual(manifest.entry_point, "hello_world:HelloWorldScreen")
        self.assertEqual(manifest.capabilities, ("screen",))

    def test_discovery_finds_example_without_importing_it(self):
        found, errors = discover_plugins(ROOT / "plugins")
        self.assertIn("hello-world", found)
        self.assertEqual(errors, {})

    def test_renderer_returns_64_by_32_frame(self):
        spec = importlib.util.spec_from_file_location("hello_world_example", EXAMPLE / "hello_world.py")
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        frame = module.HelloWorldScreen().render()
        self.assertIsInstance(frame, Framebuffer)
        self.assertEqual((frame.width, frame.height), (64, 32))
        self.assertEqual(len(frame.ppm()), len(b"P6\n64 32\n255\n") + 64 * 32 * 3)

    def test_renderer_is_deterministic(self):
        spec = importlib.util.spec_from_file_location("hello_world_example", EXAMPLE / "hello_world.py")
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        screen = module.HelloWorldScreen()
        self.assertEqual(screen.render().ppm(), screen.render().ppm())


if __name__ == "__main__":
    unittest.main()
