# v0.6.0 English Football Release Checklist

Status: **release candidate; automated regression reported green (1,158 tests, October 17, 2026); live ESPN acceptance and Pi 3 deployment checks outstanding**. Do not tag or promote until acceptance is complete.

## Scope
- Premier League (EPL), Championship, League One, League Two.
- English Football is **disabled by default** on existing and new installations.
- Stable ESPN club IDs survive division changes; favorite club selection and four division toggles appear in the dashboard.
- Existing MLB/NHL/NBA/WNBA/NFL/MLS/NWSL functionality and live-game priority must remain unchanged.
- Live match summaries enrich goal IDs, scorer (when unambiguous), team and minute. No summary requests occur in the renderer.

## Development Pi acceptance
1. Update to the latest `feature/0.6.0-english-football` commit via System → Software Updates.
2. Run `python3 -m unittest discover -s tests -p 'test_*.py'` and record total, skips and failures.
3. Run `python3 -m unittest tests.test_english_match_acceptance tests.test_english_goal_enrichment tests.test_english_summary -v`.
4. Inspect the dashboard: English disabled by default; division selection, favorites and settings persist; existing sports still work.
5. Check the board emulator in both no-live and simulated live modes; live fixtures suppress news/time/weather and non-live matches.
6. Confirm service health and logs: `sudo ulsctl health`, `sudo ulsctl status`, `sudo ulsctl logs`.

## Acceptance evidence and limitations
- Development Pi full-suite run reported by tester: **1,158 tests passed**, October 17, 2026. This is user-reported device execution, not CI attestation.
- Simulated lifecycle, duplicate suppression, temporary summary outages, legacy v0.5 settings and release metadata covered by tests.
- Historical ESPN summary probes verified 11 goal IDs and 7 scorer names; **no live ESPN goal event has been observed**.
- Hardware Pi 3 deployment of this branch, updater rollback, and real live timing remain unverified. The candidate has not been deployed or tagged.

## Real ESPN live acceptance (not yet verified)
- Observe a scheduled English match becoming live, halftime and final.
- Verify clock/score updates and a **new** goal summary event arrives while live.
- Confirm goal screen appears once for a new official event ID and expires back to match view.
- Confirm initial historical goals do not replay at worker startup, duplicate summary polls do not replay goals, and an ESPN summary outage does not blank scores.
- Record division, fixture, date, observed clock and goal latency. If live events are absent, do not claim live goal alerts are validated.

## Release and Pi 3 rollout
1. Keep production on the known-good v0.5.0 release until checks above pass.
2. Verify clean working tree and matching release metadata; change `__version__` from `0.6.0.dev0` to `0.6.0` **only when ready to release**.
3. Merge reviewed branch into main, tag `v0.6.0`, and use the existing dashboard updater to install on the Pi 3.
4. Before update, preserve a known-good recovery card/backup; do not overwrite saved `/etc/uls` configuration or `/var/lib/uls` data.
5. First boot: leave English disabled, verify existing sports, physical 64×32 board, web login, `sudo ulsctl health` and logs.
6. Enable English after confirmation and verify league/favorite settings, worker startup and display.
7. If regression or boot failure occurs, revert using the updater's supported rollback path or the known-good recovery image, then check services and config.

**No production deployment or release tag is authorized by this checklist alone.**
