"""Pure ESPN English football summary keyEvents goal adapter.

No network calls; no fabricated IDs or scorers. The summary endpoint exposes
scoringPlay and official event IDs independently of the scoreboard endpoint.
"""
from collections.abc import Mapping
from .soccer import SoccerGoal


def parse_key_event_goals(payload):
    """Return credited goal events from a match-summary response."""
    if not isinstance(payload, Mapping):
        raise ValueError("Expected ESPN summary object")
    events = payload.get("keyEvents") or []
    if not isinstance(events, list):
        return ()
    goals = []
    seen = set()
    for event in events:
        if not isinstance(event, Mapping) or event.get("scoringPlay") is not True:
            continue
        event_id = event.get("id")
        if event_id is None or not str(event_id).strip() or str(event_id) in seen:
            continue
        seen.add(str(event_id))
        team = event.get("team") or {}
        if not isinstance(team, Mapping):
            team = {}
        team_id = str(team.get("abbreviation") or team.get("id") or "").strip().upper()
        clock = event.get("clock") or {}
        minute = clock.get("displayValue") if isinstance(clock, Mapping) else None
        participants = event.get("participants") or []
        scorer = None
        if isinstance(participants, list):
            for participant in participants:
                if not isinstance(participant, Mapping):
                    continue
                role = str(participant.get("type") or participant.get("role") or "").lower()
                if role not in ("scorer", "goal", "goal scorer"):
                    continue
                athlete = participant.get("athlete") or participant.get("player") or {}
                if isinstance(athlete, Mapping):
                    scorer = athlete.get("displayName") or athlete.get("fullName")
                if scorer:
                    break
            # ESPN English summaries omit roles on many goal events. A
            # single participant is unambiguous; multiple untyped people are not.
            if scorer is None and len(participants) == 1:
                participant = participants[0]
                if isinstance(participant, Mapping) and not participant.get("type") and not participant.get("role"):
                    athlete = participant.get("athlete") or {}
                    if isinstance(athlete, Mapping):
                        scorer = athlete.get("displayName") or athlete.get("fullName")
        goals.append(SoccerGoal(event_id=str(event_id), team_id=team_id,
                                scorer=scorer,
                                minute=str(minute) if minute is not None else None,
                                own_goal=bool(event.get("ownGoal", False))))
    return tuple(goals)
