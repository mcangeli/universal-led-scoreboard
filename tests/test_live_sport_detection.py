"""Live-game detection must examine all eligible cached games."""
import unittest
from types import SimpleNamespace
from universal_led.nhl_engine import ConfiguredNHLRenderer
from universal_led.nba_engine import ConfiguredNBARenderer
from universal_led.wnba_engine import ConfiguredWNBARenderer
from universal_led.nfl_engine import ConfiguredNFLRenderer


class CachedFeed:
    def __init__(self, games):
        self._games = games
    def games(self):
        return self._games


class LiveDetectionTests(unittest.TestCase):
    def test_no_games(self):
        for cls in (ConfiguredNHLRenderer, ConfiguredNBARenderer,
                    ConfiguredWNBARenderer, ConfiguredNFLRenderer):
            with self.subTest(renderer=cls.__name__):
                self.assertFalse(cls(CachedFeed([])).has_live_games())

    def test_wnba_inherits_live_check(self):
        self.assertIs(ConfiguredWNBARenderer.has_live_games,
                      ConfiguredNBARenderer.has_live_games)


if __name__ == "__main__":
    unittest.main()
