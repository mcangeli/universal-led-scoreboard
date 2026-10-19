"""Automatic sports news with independent per-league controls.

A failed provider cannot interrupt game rendering or other news sources.
English football owns EFL fixtures; EFL news is a separate optional feed.
"""
from .mlb_news import MLBNewsFeed
from .nhl_news import NHLNewsFeed
from .nba_news import NBANewsFeed
from .wnba_news import WNBANewsFeed
from .nfl_news import NFLNewsFeed
from .soccer_news import SoccerNewsFeed

SUPPORTED_NEWS = ('mlb', 'nhl', 'nba', 'wnba', 'nfl', 'mls', 'nwsl', 'english', 'efl')
EFL_COMPETITIONS = frozenset(('CHAMPIONSHIP', 'LEAGUE_ONE', 'LEAGUE_TWO'))


class AutomaticSportsNews:
    def __init__(self, providers=None):
        self.providers = ({
            'mlb': MLBNewsFeed(), 'nhl': NHLNewsFeed(),
            'nba': NBANewsFeed(), 'wnba': WNBANewsFeed(),
            'nfl': NFLNewsFeed(), 'mls': SoccerNewsFeed('mls'),
            'nwsl': SoccerNewsFeed('nwsl'),
            'english': SoccerNewsFeed('english'),
            'efl': SoccerNewsFeed('efl'),
        } if providers is None else dict(providers))

    def _headlines(self, sport):
        provider = self.providers.get(sport)
        if provider is None:
            return []
        try:
            return provider.items()
        except (OSError, ValueError):
            return []

    def items(self, settings):
        headlines = []
        for sport, options in settings['sports'].items():
            if sport != 'efl' and options['enabled'] and options.get('news_enabled', sport == 'mlb'):
                headlines.extend(self._headlines(sport))

        english = settings['sports'].get('english', {})
        efl = settings['sports'].get('efl', {})
        leagues = settings.get('english', {}).get('enabled_leagues', ())
        if (english.get('enabled') and efl.get('news_enabled')
                and EFL_COMPETITIONS.intersection(leagues)):
            headlines.extend(self._headlines('efl'))
        return headlines
