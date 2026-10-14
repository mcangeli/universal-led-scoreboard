"""Shared live settings snapshot for native configurator and MLB preview."""
import threading
import time
from .sport_settings import load_settings
from .mlb_runtime import select_games
from .mlb_palette_v11 import MLBPaletteScreen
from .mlb_classic import BaseballGame
from .config_store import read_config

class ConfiguredMLBRenderer:
    def __init__(self,directory,feed):
        self.directory=directory
        self.feed=feed
        self._lock=threading.Lock()
        self._started=time.monotonic()
        self._settings=load_settings(directory)

    def settings(self):
        with self._lock:
            return self._settings

    def apply(self,settings):
        with self._lock:
            self._settings=settings
            self._started=time.monotonic()

    def game(self):
        settings=self.settings()['mlb']
        games=select_games(self.feed.games(),settings['favorite_team'],settings['mode'])
        if not games:
            return BaseballGame()
        with self._lock:
            index=int((time.monotonic()-self._started)//settings['rotation_seconds'])%len(games)
        return games[index]

    def frame(self):
        palette=read_config(self.directory)
        return MLBPaletteScreen(self.game(),palette['teams'],palette['scoreboard']).render()
