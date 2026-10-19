"""NBA season calendar adapter for explicitly verified provider boundaries."""
import json
from urllib.request import Request, urlopen

from .nba_season_calendar import parse_nba_season_windows


def fetch_nba_season_windows(_competition, *, url, opener=None, timeout=8):
    """Fetch a configured JSON calendar; never fabricate missing boundaries.

    The endpoint must return {'seasons': [{'regularSeasonStartDate': YYYY-MM-DD,
    'regularSeasonEndDate': YYYY-MM-DD}]}. No default endpoint is assumed.
    """
    if not isinstance(url, str) or not url.startswith('https://'):
        raise ValueError('NBA season calendar requires a verified HTTPS provider URL')
    opener = opener or urlopen
    request = Request(url, headers={'Accept': 'application/json',
                                    'User-Agent': 'UniversalLEDScoreboard/0.7'})
    with opener(request, timeout=timeout) as response:
        return parse_nba_season_windows(json.load(response))
