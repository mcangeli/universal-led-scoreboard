# v0.5.0 MLS/NWSL release acceptance

Status: **release candidate, not tagged or merged**. This checklist separates verified automated behavior from observations that still need to happen on a real device or live feed.

## Confirmed

- [x] Raspberry Pi 5 updater candidate validation: 1,043 tests, 15 skipped, no failures (reported October 17, 2026).
- [x] Raspberry Pi 3 preflight healthy: Trixie, web and matrix services active, fresh frame, clean working tree; /etc/uls, /var/lib/uls and service definitions backed up and archives verified.
- [x] MLS/NWSL 64×32 emulator layout visually reviewed, including first-half stoppage time.
- [x] Fixture-based parser coverage for scores, statuses, goal metadata, period/clock and malformed feed fields.
- [x] Combined MLS/NWSL fixture tests for favorites, live-game priority, halftime, scheduled and final screens.
- [x] Regression coverage for duplicate goal IDs and halftime goal suppression.
- [x] News controls for MLS and NWSL covered by automated tests.
- [x] Live MLS halftime display: CLT–PHI showed `HT` after ESPN state/name parsing fix (user confirmed October 17, 2026).

## Provider strategy (confirmed decision)

- Prefer **league-specific MLS and NWSL sources** when a stable, permitted, validated endpoint and adapter are available.
- Keep the currently working ESPN scoreboard feeds as the v0.5.0 baseline and fallback; do not switch an unverified provider into production.
- MLS and NWSL must have separate adapters and contract tests, since league response schemas may differ.
- Use the existing `SoccerProviderRouter` policy: valid empty primary results are authoritative; provider failures may fall back to ESPN. Log active provider and last primary error for diagnosis.
- Before enabling a league-specific adapter, verify endpoint availability, licensing/terms, scores, status/clock, team identifiers, goal events, and failure behavior against live data.
- Future configurator work: surface active provider and fallback state without exposing secrets.

## Outstanding before v0.5.0 tag

- [ ] Complete current ESPN MLS and NWSL live-feed verification: MLS CLT–PHI halftime is confirmed, but NWSL, team IDs, other status values, second-half restart and final transitions still need observation.
- [ ] Observe an actual scoring event and credited scorer (including whether provider supplies `details` and stable goal IDs). Verify goal announcement timing on the board.
- [ ] With MLS and NWSL both enabled, check favorite-team persistence after dashboard save/reload and simultaneous live-match rotation.
- [ ] Confirm live games suppress news, weather and time; verify supplemental screens resume when all eligible live games end.
- [ ] Check board preview and physical 64×32 matrix if available, including long names and two-digit scores.
- [ ] Run `sudo ulsctl health`, `sudo ulsctl status` and verify both services after a restart.
- [ ] Review release diff, license/attribution and changelog; merge into `main` and tag `v0.5.0` only after acceptance.

## Device checks

Use **System → Software Updates** to install the branch; candidate tests must pass before the updater changes the installation. Check **Open Board View** and sport/news settings. For diagnostics:

```bash
sudo ulsctl health
sudo ulsctl status
sudo ulsctl logs
```

For local regression tests from the installed app directory:

```bash
python3 -m unittest discover -s tests -p 'test_*.py'
```

If no MLS or NWSL game is live, do not mark live transitions as verified merely because a fixture test passes. Wait for a game or use a clearly labeled simulated test.
