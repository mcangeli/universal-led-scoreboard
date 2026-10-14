"""Screen rotation and display dimensions."""
from dataclasses import dataclass
from typing import Protocol

class Screen(Protocol):
    name: str
    def render(self, canvas: 'Canvas') -> None: ...

@dataclass(frozen=True)
class Canvas:
    width: int = 64
    height: int = 32
    def __post_init__(self):
        if self.width < 1 or self.height < 1:
            raise ValueError('Canvas dimensions must be positive')

class Rotation:
    def __init__(self, screens: list[Screen]):
        self.screens = list(screens)
        self.index = 0
    def next(self) -> Screen:
        if not self.screens:
            raise RuntimeError('No screens configured')
        screen = self.screens[self.index % len(self.screens)]
        self.index += 1
        return screen
