"""Shared live settings snapshot for native configurator and MLB preview."""
import threading
import time
from pathlib import Path
from .sport_settings import load_settings, validate_settings
from .mlb_runtime import select_games
from .mlb_palette_v11 import MLBPaletteScreen
from .mlb_live_details import MLBLiveDetailsScreen
from .mlb_previous_play import MLBPreviousPlayScreen
from .mlb_classic import BaseballGame
from .display import splash
from .news_screen import NewsHeadlineScreen
from .clock_screen import ClockScreen
from .weather_screen import WeatherScreen
from .time_weather_settings import load_time_weather
from .config_store import read_config
from .screen_rotation import choose_screen
from .season_countdown_settings import current as current_countdown
from .season_countdown_screen import SeasonCountdownScreen
from .mlb_opening_feed import MLBOpeningDayFeed

class ConfiguredMLBRenderer:
    def __init__(self,directory,feed,news=None,weather=None):
        self.directory=directory
        self.feed=feed
        self.news=news
        self.weather=weather
        self.opening_feed=MLBOpeningDayFeed()
        self._lock=threading.Lock()
        self._started=time.monotonic()
        self._supplemental_stride=1
        self._settings=load_settings(directory)

    def settings(self):
        with self._lock:
            return self._settings

    def apply(self,settings):
        with self._lock:
            # Some older callers overlay favorite_team onto a default settings dict.
            # Honor that explicit legacy override when both spellings are present.
            if 'favorite_team' in settings.get('mlb',{}):
                settings={**settings,'mlb':{**settings['mlb']}}
                settings['mlb']['favorite_teams']=[settings['mlb'].pop('favorite_team')]
            self._settings=validate_settings(settings)
            self._started=time.monotonic()

    def set_supplemental_stride(self, stride):
        """Advance supplemental slots once per MLB appearance in multisport mode."""
        if not isinstance(stride, int) or stride < 1:
            raise ValueError('stride must be a positive integer')
        with self._lock:
            self._supplemental_stride=stride
            self._started=time.monotonic()

    def _selection(self):
        """Keep game and pregame page on the same rotation clock."""
        settings=self.settings()['mlb']
        all_games=self.feed.games()
        favorites=set(settings.get('favorite_teams',settings.get('favorite_team',['ATL'])))
        selected=select_games(all_games,settings.get('favorite_teams',settings.get('favorite_team',['ATL'])),settings['mode'])
        favorite_live=[g for g in all_games if g.status=='live' and (g.away in favorites or g.home in favorites)]
        all_live=[g for g in all_games if g.status=='live']
        mode=settings['mode']
        if mode=='favorite':
            games=favorite_live or selected
        elif mode=='fallback':
            games=favorite_live or all_live or selected
        else:
            games=all_live or selected
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
        if game.status=='live':
            classic=settings.get('live_classic_percent',50)
            matchup=settings.get('live_matchup_percent',25)
            play=100-classic-matchup
            has_matchup=any(value is not None for value in (
                game.pitcher,game.batter,game.balls,game.strikes,
                game.pitch_count,game.pitch_speed_mph))
            weights=[(0,classic)]
            if matchup>0 and has_matchup:
                weights.append((3,matchup))
            if play>0 and (game.previous_play or '').strip():
                weights.append((4,play))
            total=sum(weight for _,weight in weights)
            position=within/slot*total
            cumulative=0
            for selected,weight in weights:
                cumulative+=weight
                if position<cumulative:
                    page=selected
                    break
        return game,page

    def has_games(self):
        return bool(self.feed.games())

    def game(self):
        return self._selection()[0]

    def frame(self):
        palette=read_config(self.directory)
        game,page=self._selection()
        if game is None or game.status!='live':
            preferences=load_time_weather(self.directory)
            clock_enabled=preferences['clock_enabled'] and (Path(self.directory)/'time_weather.json').exists()
            snapshot=self.weather.snapshot() if preferences['weather_enabled'] and self.weather is not None else None
            headlines=self.news.items() if self.news is not None else []
            with self._lock:
                elapsed=max(0.0,time.monotonic()-self._started)
            slot=self.settings()['mlb']['rotation_seconds']
            opening = current_countdown(self.directory, season_active=game is not None,
                                        provider=self.opening_feed)
            selected=choose_screen(int(elapsed//(slot*self._supplemental_stride)),has_game=game is not None,
                                   clock=clock_enabled,weather=snapshot is not None,
                                   news=bool(headlines),countdown=opening is not None)
            if selected=='countdown':
                return SeasonCountdownScreen(opening).render()
            if selected=='clock':
                return ClockScreen(preferences['timezone'],preferences['time_format']).render()
            if selected=='weather':
                return WeatherScreen(snapshot,preferences['temperature_unit']).render()
            if selected=='news':
                options=self.settings()['news']
                duration=options['headline_seconds']
                local=elapsed%slot
                index=int(elapsed//slot)%len(headlines)
                offset=int((local%duration)*options['scroll_chars_per_second'])
                item=headlines[index]
                return NewsHeadlineScreen(item.text,item.source,offset=offset).render()
            if selected=='splash':
                return splash()
        if not game:
            return splash()
        if page==3:
            with self._lock:
                elapsed=max(0.0,time.monotonic()-self._started)
            # About three glyphs per second; short surnames remain stationary.
            offset=int(elapsed*3)
            return MLBLiveDetailsScreen(game,palette['scoreboard'],offset=offset).render()
        if page==4:
            with self._lock:
                elapsed=max(0.0,time.monotonic()-self._started)
            slot=self.settings()['mlb']['rotation_seconds']
            within=elapsed%slot
            mlb=self.settings()['mlb']
            classic=mlb.get('live_classic_percent',50)
            matchup=mlb.get('live_matchup_percent',25)
            play=100-classic-matchup
            has_matchup=any(value is not None for value in (
                game.pitcher,game.batter,game.balls,game.strikes,
                game.pitch_count,game.pitch_speed_mph))
            total=classic+(matchup if has_matchup else 0)+play
            play_start=slot*(total-play)/total
            offset=int(max(0,within-play_start)*5)
            return MLBPreviousPlayScreen(game,offset,palette['scoreboard']).render()
        return MLBPaletteScreen(game,palette['teams'],palette['scoreboard'],pregame_page=page).render()
