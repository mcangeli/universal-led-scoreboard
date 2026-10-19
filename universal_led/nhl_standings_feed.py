"""Normalize official NHL standings without importing the archived LED project's API.

NHL standings use regulation losses and overtime losses separately. Standing.draws
holds OTL only for compatibility with the shared standings model; NHL rendering
must label this field OTL, never draws.
"""
from __future__ import annotations

from .standings import Standing


def parse_nhl_standings(payload):
    """Return official division-ranked NHL rows from a standings/now payload."""
    if not isinstance(payload, dict) or not isinstance(payload.get("standings"), list):
        raise ValueError("Invalid NHL standings response")
    rows = []
    for item in payload["standings"]:
        if not isinstance(item, dict):
            continue
        division = item.get("divisionName")
        if isinstance(division, dict):
            division = division.get("default")
        abbreviation = item.get("teamAbbrev")
        if isinstance(abbreviation, dict):
            abbreviation = abbreviation.get("default")
        rank = item.get("divisionSequence")
        wins = item.get("wins")
        losses = item.get("losses")
        overtime_losses = item.get("otLosses")
        played = item.get("gamesPlayed")
        points = item.get("points")
        if (not isinstance(division, str) or not division.strip()
                or not isinstance(abbreviation, str) or not abbreviation.strip()
                or any(type(value) is not int or value < 0
                       for value in (rank, wins, losses, overtime_losses, played, points))
                or rank < 1):
            continue
        rows.append(Standing(
            league="NHL", group=division.strip(), team_id=abbreviation.strip().upper(),
            abbreviation=abbreviation.strip().upper()[:3],
            played=played, wins=wins, losses=losses, draws=overtime_losses,
            points=points, rank=rank))
    return tuple(rows)


NHL_STANDINGS_URL = "https://api-web.nhle.com/v1/standings/now"
NHL_DIVISIONS = ("Atlantic", "Metropolitan", "Central", "Pacific")


def fetch_nhl_standings(_league="NHL", *, opener=None, timeout=12):
    """Fetch NHL official standings for a background cache worker only."""
    import json
    from urllib.request import urlopen

    if opener is None:
        opener = urlopen
    with opener(NHL_STANDINGS_URL, timeout=timeout) as response:
        payload = json.load(response)
    return parse_nhl_standings(payload)


def fetch_nhl_division(division, *, fetcher=fetch_nhl_standings):
    """Provide one division to a persistent standings cache."""
    if division not in NHL_DIVISIONS:
        raise ValueError("Unknown NHL division")
    return tuple(row for row in fetcher("NHL") if row.group == division)


NHL_WILD_CARD_GROUPS = ('Eastern_Wild_Card', 'Western_Wild_Card')


def parse_nhl_wild_card(payload):
    """Top five wildcard-eligible clubs per conference, by official ordering.

    The top three teams in each division qualify through their division and
    are excluded. NHL conferenceSequence provides the league's official
    conference ordering, including its tiebreakers.
    """
    if not isinstance(payload, dict) or not isinstance(payload.get('standings'), list):
        raise ValueError('Invalid NHL standings response')
    eligible = {group: [] for group in NHL_WILD_CARD_GROUPS}
    for item in payload['standings']:
        if not isinstance(item, dict):
            continue
        conference = item.get('conferenceName')
        if isinstance(conference, dict):
            conference = conference.get('default')
        group = {'Eastern': 'Eastern_Wild_Card',
                 'Western': 'Western_Wild_Card'}.get(conference)
        if group is None:
            continue
        division_rank = item.get('divisionSequence')
        conference_rank = item.get('conferenceSequence')
        fields = (division_rank, conference_rank, item.get('wins'),
                  item.get('losses'), item.get('otLosses'),
                  item.get('gamesPlayed'), item.get('points'))
        if any(type(value) is not int or value < 0 for value in fields):
            continue
        if division_rank < 1 or conference_rank < 1 or division_rank <= 3:
            continue
        abbreviation = item.get('teamAbbrev')
        if isinstance(abbreviation, dict):
            abbreviation = abbreviation.get('default')
        if not isinstance(abbreviation, str) or not abbreviation.strip():
            continue
        eligible[group].append((conference_rank, item, abbreviation.strip().upper()))
    rows = []
    for group in NHL_WILD_CARD_GROUPS:
        for rank, (_, item, abbreviation) in enumerate(
                sorted(eligible[group], key=lambda entry: entry[0])[:5], 1):
            rows.append(Standing(
                league='NHL', group=group, team_id=abbreviation,
                abbreviation=abbreviation[:3], rank=rank,
                played=item['gamesPlayed'], wins=item['wins'],
                losses=item['losses'], draws=item['otLosses'],
                points=item['points']))
    return tuple(rows)


def fetch_nhl_wild_card(group, *, fetcher=None):
    if group not in NHL_WILD_CARD_GROUPS:
        raise ValueError('Unknown NHL wild card group')
    if fetcher is None:
        import json
        from urllib.request import urlopen
        with urlopen(NHL_STANDINGS_URL, timeout=12) as response:
            payload = json.load(response)
        rows = parse_nhl_wild_card(payload)
    else:
        rows = fetcher()
    return tuple(row for row in rows if row.group == group)
