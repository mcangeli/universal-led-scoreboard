# v0.7.0 Scoring and Standings Release Checklist

Status: **release candidate, not merged or tagged** (October 18, 2026).

## Scope

- Live-game and scoring alert priority; eligible live games suppress news, clock, weather and standings.
- Scheduled and final games remain in the game rotation when eligible; idle standings appear only when no eligible games remain.
- Idle news alternates with standings without skipping standings pages.
- Standings refresh runs through the cache/background worker and retains the last good rows on provider failures.
- MLB R/H/E one- and two-digit totals have readable gutters and centered column alignment.
- Browser preview scales to mobile width while preserving 64×32 proportions.

## Acceptance evidence

- [x] Raspberry Pi 5 candidate updater: **1,312 tests passed, 15 skipped**, user-reported October 18, 2026.
- [x] EPL live game: clock progression, halftime, second half, added time and final rotation observed.
- [x] MLB R/H/E improved alignment visually reviewed after pixel test corrections.
- [x] Standings outage and recovery covered by deterministic regression tests.
- [x] Live → final → idle standings → new eligible game priority covered by deterministic regression tests.
- [ ] Confirm standings pages against actual provider responses on the device.
- [ ] Observe a real scoring event and alert on the production Pi 3; no live score event has yet been confirmed.
- [x] Visual review of latest MLB R/H/E alignment and board layouts reported satisfactory on October 18, 2026; physical-matrix-specific confirmation is not separately established.
- [x] Production-target Pi 3: user reports successful candidate update installation and all sports enabled (October 18, 2026). Configuration retention and ongoing physical display behavior still require observation.
- [ ] Check licenses/attributions and changelog/README accuracy.
- [x] Updater candidate preflight: 1,312 tests passed, 15 skipped, user-confirmed October 18, 2026 (prior to documentation-only commits).
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
