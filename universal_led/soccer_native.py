"""Native league match normalization.

Use only documented fields. Native match collections are not ESPN events.
Goal scorers are deliberately absent until official event feeds are verified.
"""
from collections.abc import Mapping
from .soccer import SoccerMatch

MLS_STATUS = {
    "live": "live", "inprogress": "live", "halftime": "live",
    "fulltime": "post", "final": "post", "finished": "post",
    "prematch": "pre", "scheduled": "pre",
}
NWSL_STATUS = {
    "live": "live", "prematch": "pre", "postmatch": "post",
}


def _rows(payload):
    if isinstance(payload, list):
        return payload
    if isinstance(payload, Mapping):
        for key in ("data", "matches", "items"):
            value = payload.get(key)
            if isinstance(value, list):
                return value
    raise ValueError("Unrecognized native match collection")


def _score(value):
    if value is None:
        return 0
    return int(value)


def parse_mls_matches(payload):
    matches = []
    for row in _rows(payload):
        if not isinstance(row, Mapping):
            raise ValueError("Invalid MLS match record")
        match_id = row.get("matchId", row.get("match_id"))
        home = row.get("homeTeamThreeLetterCode", row.get("home_team_three_letter_code"))
        away = row.get("awayTeamThreeLetterCode", row.get("away_team_three_letter_code"))
        if not match_id or not home or not away:
            raise ValueError("MLS match missing required identifiers")
        status = str(row.get("matchStatus", row.get("match_status", "scheduled")))
        matches.append(SoccerMatch(
            str(match_id), "MLS", str(home), str(away),
            _score(row.get("homeTeamGoals", row.get("home_team_goals"))),
            _score(row.get("awayTeamGoals", row.get("away_team_goals"))),
            MLS_STATUS.get(status.lower().replace(" ", ""), "unknown"),
        ))
    return tuple(matches)


def parse_nwsl_matches(payload):
    matches = []
    for row in _rows(payload):
        if not isinstance(row, Mapping):
            raise ValueError("Invalid NWSL match record")
        match_id = row.get("matchId", row.get("match_id"))
        # SDP match collection exposes team IDs; team abbreviations require
        # a separately verified season team lookup.
        home = row.get("homeTeamId", row.get("home_team_id"))
        away = row.get("awayTeamId", row.get("away_team_id"))
        if not match_id or not home or not away:
            raise ValueError("NWSL match missing team IDs; team mapping required")
        status = str(row.get("status", "unknown")).lower()
        matches.append(SoccerMatch(
            str(match_id), "NWSL", str(home), str(away),
            _score(row.get("homeScorePush", row.get("home_score_push"))),
            _score(row.get("awayScorePush", row.get("away_score_push"))),
            NWSL_STATUS.get(status, "unknown"),
        ))
    return tuple(matches)
