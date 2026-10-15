"""Automatic official-news providers for sports modules.

A missing provider returns no headlines, never an error to the score renderer.
Network-backed providers remain independent from game feeds.
"""
from .mlb_news import MLBNewsFeed

SUPPORTED_NEWS = ('mlb',)


class AutomaticSportsNews:
    def __init__(self, providers=None):
        self.providers = {'mlb': MLBNewsFeed()} if providers is None else dict(providers)

    def items(self, settings):
        headlines = []
        for sport, options in settings['sports'].items():
            if options['enabled'] and options.get('news_enabled', sport == 'mlb'):
                provider = self.providers.get(sport)
                if provider is not None:
                    try:
                        headlines.extend(provider.items())
                    except (OSError, ValueError):
                        continue
        return headlines
