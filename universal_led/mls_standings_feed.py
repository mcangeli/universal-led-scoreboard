"""MLS standings adapter using the existing soccer standings parser."""

from .football_standings_feed import parse_football_standings

MLS_COMPETITION = "usa.1"


def parse_mls_standings(payload):
    """Normalize MLS conference records without changing the shared renderer."""
    return parse_football_standings(payload, "MLS")
