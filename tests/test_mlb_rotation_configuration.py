import threading
import unittest
from unittest.mock import patch
from universal_led.mlb_classic import BaseballGame
from universal_led.runtime_settings import ConfiguredMLBRenderer
from universal_led.sport_settings import DEFAULT_SETTINGS, validate_settings


class MLBRotationConfigurationTests(unittest.TestCase):
    def test_legacy_settings_are_upgraded(self):
        import copy
        old=copy.deepcopy(DEFAULT_SETTINGS)
        del old['mlb']['live_classic_percent']
        del old['mlb']['live_matchup_percent']
        new=validate_settings(old)
        self.assertEqual(new['mlb']['live_classic_percent'],50)
        self.assertEqual(new['mlb']['live_matchup_percent'],25)

    def test_invalid_allocation_rejected(self):
        import copy
        settings=copy.deepcopy(DEFAULT_SETTINGS)
        settings['mlb']['live_classic_percent']=80
        settings['mlb']['live_matchup_percent']=30
        with self.assertRaises(ValueError):
            validate_settings(settings)

    def test_custom_split_changes_live_pages(self):
        import copy
        settings=copy.deepcopy(DEFAULT_SETTINGS)
        settings['mlb'].update(mode='all',rotation_seconds=20,
                               live_classic_percent=70,live_matchup_percent=10)
        renderer=ConfiguredMLBRenderer.__new__(ConfiguredMLBRenderer)
        renderer._lock=threading.Lock()
        renderer._started=100
        renderer._settings=settings
        class Feed:
            def games(self):
                return [BaseballGame(status='live',pitcher='Max Fried',
                                     previous_play='Fly out to center')]
        renderer.feed=Feed()
        for elapsed,expected in ((10,0),(15,3),(18,4)):
            with self.subTest(elapsed=elapsed):
                with patch('universal_led.runtime_settings.time.monotonic',
                           return_value=100+elapsed):
                    self.assertEqual(renderer._selection()[1],expected)


if __name__=='__main__':
    unittest.main()
