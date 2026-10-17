# v0.6.0 English football provider plan

Status: ESPN four-division fixture endpoint validation passed on Pi 5 (2026-10-17); live score/event contract and implementation remain pending.

## Scope
Four independent competitions: Premier League, EFL Championship, EFL League One and EFL League Two. Club identity is independent of seasonal competition membership, preserving favorites across promotion and relegation.

## Provider policy
- ESPN is the primary provider for match fixtures, scores, status, clock and events.
- A secondary English football provider (candidate: API-Football; not yet contracted or enabled) may confirm daily schedules, competition activity, and match statuses where supported by verified licensing, quotas and coverage.
- ESPN healthy live scores and goal events remain authoritative. Disagreement is diagnostic information, not permission to replace good primary data.
- Primary failures may fall back to validated secondary data only when competition, season, fixture identity, freshness and fields have been matched. Never synthesize live goal events from a schedule-only source.
- An empty but valid ESPN schedule is not necessarily an error; check date/competition context before supplementing.
- Cache secondary requests and enforce per-provider quota budgets. Never require a paid key for the baseline scoreboard to function.
- Surface source, freshness and fallback state in diagnostics without revealing secrets.

## Dev device verification (2026-10-17)

Read-only `scripts/probe-english-football.py 2026-10-17` executed on Scoreboard Dev (Pi 5): EPL `eng.1` 5/5 valid events; Championship `eng.2` 11/11; League One `eng.3` 11/11; League Two `eng.4` 12/12. Total 39 events. This proves accessible fixtures with event IDs and home/away competitors for that date, not live score or goal-event reliability.

## Validation gate before feature implementation
1. [x] Verify ESPN endpoints for all four competitions with actual 2026-27 fixtures, including League Two (39 valid events on 2026-10-17).
2. Confirm kickoff timezone, club identifiers, scores, status transitions, postponements and scorer/event availability.
3. Verify secondary API terms, coverage, rate limits and historical/seasonal IDs before enabling it.
4. Build provider contract tests with fixture samples and simulate conflicting, empty, stale and failed responses.
5. Preserve MLS/NWSL and all existing sports behavior through regression tests.

## Release acceptance
Physical 64x32 readability, favorite persistence across season changes, combined competition rotation, live-game priority and no-match fallback. Observe real match transitions where possible and label unobserved cases as fixture-tested only.
