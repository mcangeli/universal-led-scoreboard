"""Use the configured game-selection policy for global scoring alerts."""


def scoring_event_eligible(event, settings):
    """Reject alerts from disabled leagues or games excluded by favorite-only mode.

    A favorite matchup is eligible regardless of which team scored. Other
    selection modes preserve the existing alert scope and fallback behavior.
    """
    sport = str(event.sport).lower()
    if sport == "soccer":
        league = str(event.league).upper()
        sport = league.lower() if league in ("MLS", "NWSL") else "english"
    if sport not in ("mlb", "nhl", "nba", "wnba", "nfl", "mls", "nwsl", "english"):
        return False
    if not settings.get("sports", {}).get(sport, {}).get("enabled", True):
        return False
    options = settings.get(sport, {})
    if options.get("mode") != "favorite":
        return True
    favorites = {str(team).upper() for team in options.get("favorite_teams", ())}
    return bool(favorites.intersection((str(event.home_team).upper(),
                                        str(event.away_team).upper())))
