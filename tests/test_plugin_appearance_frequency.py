"""Host-owned appearance preferences and scheduler regression checks."""
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from universal_led.plugin_settings_schema import load_settings_schema, validated_settings
from universal_led.plugin_manifest import ManifestError


class AppearanceFrequencyTests(unittest.TestCase):
    def test_default_calendar_and_other_plugins(self):
        with tempfile.TemporaryDirectory() as directory:
            for plugin_id, expected in (('daily-calendar', 10), ('hello-world', 1)):
                package = Path(directory) / plugin_id
                package.mkdir()
                (package / 'settings-schema.json').write_text('''{"fields":{"display_seconds":{"type":"integer","default":12,"min":1,"max":3600}}}''')
                fields = load_settings_schema(package)
                self.assertEqual(validated_settings(fields, {})['appearance_every_pages'], expected)
                self.assertEqual(validated_settings(fields, {'appearance_every_pages': 20})['appearance_every_pages'], 20)
                with self.assertRaises(ManifestError):
                    validated_settings(fields, {'appearance_every_pages': 101})

    def test_calendar_waits_ten_regular_pages(self):
        from universal_led.multisport_runtime import MultiSportRenderer
        class Sport:
            def frame(self): return 'base'
            def has_live_games(self): return False
        class Plugin:
            display_seconds = 5
            appearance_every_pages = 10
            def frame(self, **kwargs): return 'calendar'
        now = [0]
        board = MultiSportRenderer(Sport(), None, clock=lambda: now[0])
        board.set_bullpen_slots([Plugin()])
        for page in range(10):
            now[0] = page * 12
            self.assertEqual(board.frame(), 'base')
        now[0] = 120
        self.assertEqual(board.frame(), 'calendar')
        now[0] = 125
        self.assertEqual(board.frame(), 'base')

    def test_live_games_precede_plugins(self):
        from universal_led.multisport_runtime import MultiSportRenderer
        class Sport:
            def has_live_games(self): return True
            def frame(self): return 'live-frame'
            def game(self): return None
        class Plugin:
            display_seconds = 12
            appearance_every_pages = 10
            def frame(self, **kwargs): raise AssertionError('plugin interrupted live game')
        renderer = MultiSportRenderer(Sport(), Sport())
        renderer.set_bullpen_slots([Plugin()])
        self.assertEqual(renderer.frame(), 'live-frame')


if __name__ == '__main__':
    unittest.main()
