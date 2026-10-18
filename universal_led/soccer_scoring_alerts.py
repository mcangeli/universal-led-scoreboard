"""Translate authoritative soccer goals into shared cross-sport scoring events.

Feed refreshers call observe_match after receiving a complete match snapshot.
This adapter never guesses a goal from a score change and never polls feeds.
"""
from .scoring_alerts import ScoreEvent
from .soccer_rotation import is_live


def soccer_score_events(match):
    """Return confirmed goal events, preserving provider event IDs."""
    return tuple(
        ScoreEvent(
            sport="soccer",
            league=match.league,
            game_id=str(match.match_id),
            event_id=str(goal.event_id),
            team_id=str(goal.team_id),
            kind="OWN GOAL" if goal.own_goal else "GOAL",
            description=(goal.scorer or "").strip(),
        )
        for goal in match.goals
        if goal.event_id and goal.team_id
    )


def observe_soccer_match(alerts, match, *, favorite_teams=()):
    """Observe one snapshot, ignoring goals added outside active play.

    Still ingest non-live snapshots as baselines to avoid replay on resume.
    The shared queue owns deduplication and favorite-team filtering.
    """
    events = soccer_score_events(match)
    if not is_live(match) or match.status.strip().lower() == "halftime":
        # Record IDs without enqueuing late corrections or halftime changes.
        # The queue is disabled temporarily only for this observation.
        # A dedicated ingest-only method avoids mutating alert configuration.
        return alerts.observe(match_sport(match), match.league, str(match.match_id),
                              events, favorite_teams=()) if not alerts.enabled else _baseline_only(alerts, match, events)
    return alerts.observe("soccer", match.league, str(match.match_id),
                          events, favorite_teams=favorite_teams)


def match_sport(match):
    return "soccer"


def _baseline_only(alerts, match, events):
    key = ("soccer", match.league, str(match.match_id))
    ids = {e.event_id for e in events}
    alerts._seen.setdefault(key, set()).update(ids)
    return ()
