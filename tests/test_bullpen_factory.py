"""Integration test for a complete Bullpen-style class trio."""
import unittest

from universal_led.bullpen_factory import BullpenFactoryError, construct_bullpen_screen


class PluginConfig:
    def __init__(self, base):
        self.team = base.plugin_config["team"]


class PluginData:
    def __init__(self, config):
        self.config = config

    def update(self, force=False):
        return None


class PluginRenderer:
    def __init__(self, config, layout, colors):
        self.config = config
        self.font = layout.font("standings.font")["font"]
        self.color = colors.graphics_color("accent")

    def can_render(self, data):
        return data.config.team == "Braves"

    def render(self, data, canvas, graphics, scrolling_text_pos):
        graphics.DrawText(canvas, self.font, 1, 8, self.color, "ATL")

    def wait_time(self):
        return 0.12

    def reset(self):
        pass


class BullpenFactoryTests(unittest.TestCase):
    def test_constructs_and_renders_complete_plugin(self):
        screen = construct_bullpen_screen(
            lambda: (PluginConfig, PluginData, PluginRenderer),
            plugin_settings={"team": "Braves"},
            fonts={"standings.font": object()},
            colors={"accent": (255, 200, 0)},
        )
        frame = screen.render()
        self.assertIsNotNone(frame)
        self.assertIn((255, 200, 0), frame.pixels[1])
        self.assertEqual(screen.wait_time(), 0.12)

    def test_missing_factory_classes_rejected(self):
        with self.assertRaises(BullpenFactoryError):
            construct_bullpen_screen(lambda: (PluginConfig, PluginData))

    def test_missing_renderer_method_rejected(self):
        class Broken:
            def __init__(self, config, layout, colors):
                pass
        with self.assertRaises(BullpenFactoryError):
            construct_bullpen_screen(lambda: (PluginConfig, PluginData, Broken),
                                     plugin_settings={"team": "Braves"})


if __name__ == "__main__":
    unittest.main()
