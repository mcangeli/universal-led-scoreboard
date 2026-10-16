"""WNBA renderer using the shared basketball selection and screen."""
from .nba_engine import ConfiguredNBARenderer
from .nba_screen import NBAScreen


class ConfiguredWNBARenderer(ConfiguredNBARenderer):
    def frame(self):
        return NBAScreen(self.game(), timezone_name=self.timezone_name,
                         time_format=self.time_format, league="WNBA").render()
