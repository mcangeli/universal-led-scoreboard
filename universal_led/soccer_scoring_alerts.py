"""Translate soccer goals and confirmed live score increases into shared alerts.

The scoreboard can report a new score before provider goal-event details arrive.
Track scores per queue and fixture to announce the increase without fabricating
a scorer. Late authoritative details are baselined, not announced twice.
"""
from weakref import WeakKeyDictionary

from .scoring_alerts import ScoreEvent
from .soccer_rotation import is_live

_snapshots = WeakKeyDictionary()


def soccer_score_events(match):
    """Return identified goal events with provider IDs and credited teams."""
    return tuple(
        ScoreEvent(
            sport="soccer", league=match.league, game_id=str(match.match_id),
            event_id=str(goal.event_id), team_id=str(goal.team_id),
            kind="OWN GOAL" if goal.own_goal else "GOAL",
            description=(goal.scorer or "").strip(),
        )
        for goal in match.goals if goal.event_id and goal.team_id
    )


def observe_soccer_match(alerts, match, *, favorite_teams=()):
    """Announce live goals once, including when event details lag the score.

    Initial snapshots and non-live score corrections establish baselines.
    A score increase without a new official goal creates a team-only alert.
    Subsequent provider event IDs for that score are baselined to prevent
    duplicate announcements.
    """
    key = (match.league, str(match.match_id))
    state = _snapshots.setdefault(alerts, {})
    events = soccer_score_events(match)
    ids = frozenset(event.event_id for event in events)
    scores = (match.home_score, match.away_score)
    previous = state.get(key)
    state[key] = (scores, ids)
    if previous is None:
        return alerts.baseline("soccer", match.league, str(match.match_id), events)

    old_scores, old_ids = previous
    live = is_live(match) and match.status.strip().lower() != "halftime"
    if not live:
        return alerts.baseline("soccer", match.league, str(match.match_id), events)

    delta = (scores[0] - old_scores[0], scores[1] - old_scores[1])
    if any(change < 0 for change in delta):
        # Corrections are not goals.
        return alerts.baseline("soccer", match.league, str(match.match_id), events)

    fresh = tuple(event for event in events if event.event_id not in old_ids)
    # Provider events can arrive one poll after the updated score. Do not
    # celebrate an old goal again just because its ID became available.
    if not any(delta):
        return alerts.baseline("soccer", match.league, str(match.match_id), events)

    # Baseline the full provider snapshot first, then submit exactly one
    # event per newly scored goal. Match new official events by credited team
    # when possible, falling back to stable score-derived identities.
    alerts.baseline("soccer", match.league, str(match.match_id), events)
    pending = []
    remaining = list(fresh)
    for team, previous_score, increase in (
        (match.home_id, old_scores[0], delta[0]),
        (match.away_id, old_scores[1], delta[1]),
    ):
        for score in range(previous_score + 1, previous_score + increase + 1):
            official = next((event for event in remaining
                             if event.team_id.upper() == str(team).upper()), None)
            if official is not None:
                remaining.remove(official)
                pending.append(official)
            else:
                pending.append(ScoreEvent(
                    sport="soccer", league=match.league,
                    game_id=str(match.match_id),
                    event_id=f"score:{team}:{score}",
                    team_id=str(team), kind="GOAL"))
    # Baseline already consumed official IDs, so use a unique queue event ID
    # for the announcement while retaining the provider ID in its identity.
    announcements = tuple(ScoreEvent(
        sport=event.sport, league=event.league, game_id=event.game_id,
        event_id="announce:" + event.event_id, team_id=event.team_id,
        kind=event.kind, description=event.description,
    ) for event in pending)
    return alerts.observe("soccer", match.league, str(match.match_id),
                          announcements, favorite_teams=favorite_teams)
