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
        alerts.cancel_game("soccer", match.league, str(match.match_id))
        return alerts.baseline("soccer", match.league, str(match.match_id), events)
    return alerts.observe("soccer", match.league, str(match.match_id),
                          events, favorite_teams=favorite_teams)
