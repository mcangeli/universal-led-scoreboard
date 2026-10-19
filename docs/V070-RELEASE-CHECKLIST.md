# v0.7.0 Scoring and Standings Release Checklist

Status: **release candidate, not merged or tagged** (October 19, 2026).

## Scope

- Live-game and scoring alert priority; eligible live games suppress news, clock, weather and standings.
- Scheduled and final games remain in the game rotation when eligible; idle standings appear only when no eligible games remain.
- Idle news alternates with standings without skipping standings pages.
- Standings refresh runs through the cache/background worker and retains the last good rows on provider failures.
- MLB R/H/E one- and two-digit totals have readable gutters and centered column alignment.
- Browser preview scales to mobile width while preserving 64×32 proportions.

## Acceptance evidence

- [x] Raspberry Pi 5 development updater: **1,507 tests passed, 15 skipped**, user-reported October 19, 2026; board display visually confirmed satisfactory.
- [x] EPL live game: clock progression, halftime, second half, added time and final rotation observed.
- [x] MLB R/H/E improved alignment visually reviewed after pixel test corrections.
- [x] Standings outage and recovery covered by deterministic regression tests.
- [x] Live → final → idle standings → new eligible game priority covered by deterministic regression tests.
- [ ] Confirm standings pages against actual provider responses on the device.
- [ ] Observe a real scoring event and alert on the production Pi 3; no live score event has yet been confirmed.
- [x] Production Pi 3 live-game priority: live games rotate across enabled sports and final scores do not interrupt while live games are eligible.
- [x] Visual review of latest MLB R/H/E alignment and board layouts reported satisfactory on October 18, 2026; physical-matrix-specific confirmation is not separately established.
- [x] Production-target Pi 3: user reports successful candidate update installation, all sports enabled, and live-game rotation and sport layouts visually confirmed (October 18, 2026). Final-score and idle-standings transitions are awaiting games to finish; configuration retention is not separately verified.
- [x] README and changelog updated for v0.7.0 scope and news/standings controls.
- [ ] Complete license and attribution review (not yet independently verified).
- [x] Updater candidate preflight: 1,507 tests passed, 15 skipped, user-confirmed October 19, 2026 after dashboard regression and documentation changes.
- [ ] Merge into main and tag v0.7.0 **only after explicit approval**.

## Smoke test

1. Confirm System → Software Updates shows the expected candidate branch and commit.
2. Check an enabled live game: live game pages must take precedence over supplemental screens.
3. Observe a final game remaining eligible in the daily rotation.
4. With no eligible games, observe standings and optional news alternating, including successive standings pages.
5. Re-enable or wait for an eligible game and confirm it takes precedence.
6. Check an MLB game with two-digit hits and verify R/H/E headers and values align and do not merge.
7. Inspect the board preview on mobile and the physical 64×32 matrix.
8. Check `sudo ulsctl health` and `sudo ulsctl status` after the update.

## Rollback and safety

Use the dashboard's candidate validation before installation. Preserve the existing `/etc/uls` configuration and `/var/lib/uls` data, and retain a known-good boot card for physical-device changes. Do not treat automated unit tests as proof of physical-driver compatibility or live-feed correctness.

## Final-score handoff acceptance (original specification; see implementation tests)

- When an eligible live game becomes final, retain a pending final-score presentation until at least one **complete** display slot has actually been shown.
- Default one appearance; configurable one, two or three appearances under Sports & Rotation.
- Each finishing game gets its own opportunity, including simultaneous finishes; active games remain eligible and retain priority between presentations.
- A two-minute threshold is a scheduling/safety bound, **not** permission to silently discard a final that has never appeared.
- Count completed visible slots, not feed polls or elapsed wall-clock time; handle interruptions and renderer restarts without falsely crediting an appearance.
- After the required appearances, normal scheduled/final rotation and idle standings rules apply.
- Add deterministic scheduler regressions for one/multiple finishes, simultaneous finishes, interrupted slots, and the timeout boundary before production rollout.

Status: implementation and deterministic regression tests are present in this candidate (see `tests/test_final_score_handoff.py` and `tests/test_final_handoff_routing.py`). Physical live-to-final handoff acceptance remains pending; the original criteria above are retained as a review checklist.


## Sports polish gate (dev first; production held)

These are acceptance criteria, not a claim that each has been observed live. Automated pregame and transition tests exist, but provider-specific physical acceptance remains separate.

- [ ] Soccer pregame displays W-D-L records for both clubs and scheduled kickoff in configured local time across EPL, Championship, League One, League Two, MLS, and NWSL.
- [ ] Soccer pregame draws from cached/provider standings with correct team ID mapping; missing or stale records show a clear fallback, never invented 0-0-0.
- [ ] Pregame header identifies the competition; labels, records, and time fit 64x32 without truncation or overlap.
- [ ] Pregame, live, halftime, stoppage, interruption, final, and rotation transitions pass per-league regressions.
- [ ] All enabled sports receive pregame/live/final visual review on the Pi 5 dev board preview and physical matrix when available.
- [ ] Full test suite passes on dev, clean install/update retains configuration, and explicit sign-off precedes production deployment.

Dev workflow: commit only to feature/0.7.0-scoring-standings; validate on the dev installation. Production is intentionally held at its current installed build even if the displayed version string also reads 0.7.0.
