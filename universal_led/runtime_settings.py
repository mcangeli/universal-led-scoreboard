"""Shared live settings snapshot for native configurator and MLB preview."""
import threading
import time
from .sport_settings import load_settings
from .mlb_runtime import select_games
from .mlb_palette_v11 import MLBPaletteScreen
from .mlb_classic import BaseballGame
from .display import splash
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

    def _selection(self):
        """Keep game and pregame page on the same rotation clock."""
        settings=self.settings()['mlb']
        games=select_games(self.feed.games(),settings['favorite_team'],settings['mode'])
        if not games:
            return None,0
        with self._lock:
            elapsed=max(0.0,time.monotonic()-self._started)
        slot=settings['rotation_seconds']
        index=int(elapsed//slot)%len(games)
        game=games[index]
        # Three pages per selected game's own slot, regardless of how many
        # other games are in rotation. Live/final games have one stable page.
        within=elapsed%slot
        page=min(2,int(within*3/slot)) if game.status=='pregame' else 0
        return game,page

    def game(self):
        return self._selection()[0]

    def frame(self):
        palette=read_config(self.directory)
        game,page=self._selection()
        if not game:
            return splash()
        return MLBPaletteScreen(game,palette['teams'],palette['scoreboard'],pregame_page=page).render()
