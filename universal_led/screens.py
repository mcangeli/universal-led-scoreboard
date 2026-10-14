"""Small, explicit screen plugin contract and deterministic preview screens."""
from dataclasses import dataclass
from typing import Protocol
from .display import Framebuffer, splash

class ScreenPlugin(Protocol):
    name: str
    def render(self) -> Framebuffer: ...

@dataclass(frozen=True)
class SplashScreen:
    name: str = 'splash'
    def render(self) -> Framebuffer:
        return splash()

@dataclass(frozen=True)
class DemoGame:
    """Offline fixture; this is NOT a live MLB data feed."""
    away: str = 'NYM'
    home: str = 'ATL'
    away_runs: int = 2
    home_runs: int = 4
    inning: int = 7

@dataclass(frozen=True)
class MLBDemoScreen:
    """Temporary baseball-style layout, not yet the upstream MLB Classic renderer."""
    game: DemoGame = DemoGame()
    name: str = 'mlb-demo'
    def render(self) -> Framebuffer:
        f = Framebuffer()
        white, gold, green = (240,240,240), (238,189,74), (90,205,120)
        f.text('MLB', 23, 0, gold)
        f.text(self.game.away, 2, 9, white)
        f.text(str(self.game.away_runs), 54, 9, white)
        f.text(self.game.home, 2, 19, green)
        f.text(str(self.game.home_runs), 54, 19, green)
        f.text('IN', 3, 25, gold)
        f.text(str(self.game.inning), 24, 25, gold)
        return f
