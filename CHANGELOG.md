# Changelog

## v0.7.0 (release candidate, 2026-10-18)

### Added
- Configurable football standings rotation on the 64×32 board, including idle standings pages and news interleaving.
- Scoring alerts and live-game prioritization regression coverage across the shared scheduler.
- Cached standings refresh with recovery after transient provider failures.

### Improved
- MLB R/H/E column spacing and alignment for one- and two-digit statistics across supported layouts.
- Responsive browser board preview on narrow screens.
- Standings page sequencing when news occupies alternate idle slots.

### Validation and outstanding release gates
- Raspberry Pi 5: user-confirmed **1,311 tests passing, 15 skipped** on October 18, 2026.
- Additional live → final → idle standings → new-game priority regression added after that confirmed run; pending candidate updater validation.
- EPL live clock, halftime, second half, stoppage time and final display observed on the test board.
- Pending: final full-suite run, physical-matrix review of latest alignment, provider integration acceptance, and approval before merging or tagging. This is **not yet a tagged release**.

## v0.5.0 (release candidate, 2026-10-17)

### Added
- MLS and NWSL 64×32 match screens, favorites, configuration, automatic news and multi-sport rotation.
- Soccer match clocks, stoppage time, halftime and final status handling; goal-event parsing and deduplication.
- ESPN soccer scoreboards as the validated baseline. League-specific feeds remain future work pending endpoint and licensing verification.

### Improved
- Live-game priority across enabled sports; supplemental clock, weather and news screens yield while eligible games are live.
- Contrast protection for dark MLB and NHL team colors, including configurable MLB palette pages.
- Browser preview framebuffer parity tests and additional multi-sport regression coverage.

### Validation and release gates
- Raspberry Pi 5: 1,043 tests passed, 15 expected skips, reported October 17, 2026.
- Raspberry Pi 3 preflight: web and matrix services active, web endpoint healthy and frames fresh.
- Production /etc/uls configuration, /var/lib/uls state and systemd services backed up; archive integrity checks passed.
- Pending: production installation, physical matrix acceptance for this candidate, live NWSL and scoring transitions, and final release tag. Automated fixtures are not a substitute for these observations.

## v0.4.5 (release candidate, 2026-10-17)

### Added and improved
- Web dashboard matrix hardware controls for enable/disable, brightness, mapping, and GPIO slowdown, with persisted settings.
- Browser-based software updates with branch selection, current release-family filtering, and optional full branch list.
- Live games take precedence over scheduled games and supplemental clock, weather, and news screens across enabled sports.
- Dashboard update progress, privileged helper installation, and saved matrix-state reconciliation.

### Safety and reliability
- Candidate code is fetched and tested before deployment; remote ancestry is checked after fetch.
- Older or divergent branch switches are rejected; required updater and matrix helpers are checked.
- Failed update branch requests are discarded; post-deployment rollback restores the dashboard helper installations.
- Fresh installer defaults to main and respects saved physical-matrix state.

### Validation and outstanding acceptance
- Raspberry Pi 3: **857 tests passed, 15 skipped** on October 17, 2026.
- Physical matrix controls, dashboard software updates, and rejection of an older unsafe branch verified on Pi 3.
- Isolated rollback test executes the recovery function with Git/service side effects stubbed; real post-deployment rollback remains unverified.
- Raspberry Pi 5: clean Raspberry Pi OS Trixie installation in emulator mode succeeded; dashboard/board display remained operational after reboot.
- Installer now explicitly installs NetworkManager and permits first-run credential creation.
- Outstanding: clean physical-driver installation, license/attribution review, and release tagging. No merge to main yet.

## v0.4.0 (2026-10-16)

### Added
- NFL scoreboard with 64×32 scheduled, live, final, possession, down and distance views.
- NFL favorite teams, game-selection mode, refresh and rotation settings.
- ESPN NFL RSS headlines with an independent news toggle.
- Empty-game skipping in multi-sport rotation and backward-compatible NFL settings defaults.

### Validation
- Raspberry Pi 3: **780 tests passed, 15 skipped, no failures**. Both web and matrix services active with fresh framebuffer.
- Live NFL news and Sunday game transitions remain to be observed on the physical matrix.
- Merged into `main` via pull request #4 (merge commit `8397f9d`).


## v0.3.0 (2026-10-16)

### Added
- NBA and WNBA scoreboard modules with scheduled, live and final game displays for 64×32 RGB LED matrices.
- Configurable NBA and WNBA favorite teams, game selection modes, refresh and rotation intervals, and sport enablement through the web dashboard.
- NBA and WNBA automatic news providers with independent enable/disable controls, integrated into the shared headline rotation.
- Pregame win-loss records for NBA and WNBA when supplied by the game feed.

### Improved
- NHL scheduled-game displays show team records when available, with a safe fallback when absent.
- Shared multi-sport rotation and settings migration accommodate NBA and WNBA while preserving older configurations.

### Validation
- Full Raspberry Pi regression run: **752 tests passed, 15 skipped**.
- NBA and WNBA configuration and physical 64×32 display confirmed; NHL pregame records observed on the physical board.
- Changes merged into `main` via pull request #3 (merge commit `ab646bb`).
- Live NBA/WNBA headline delivery and complete in-game transition coverage remain follow-up checks.

## v0.2.0 (2026-10-16)

### Added
- NHL scoreboard integration, including classic and visual 64×32 layouts and favorite-team selection.
- Shared universal news rotation for MLB and NHL alongside administrator-defined RSS/Atom sources.
- Multi-sport display selection and rotation.

### Validation
- Raspberry Pi 3 production installation: **717 tests passed, 15 skipped**.
- MLB, NHL and news rotation verified on the physical matrix.
- Web and matrix system services verified after reboot.

## 0.1.0 preview (unreleased)

### Added
- Native 64×32 MLB Classic, matchup and previous-play screens with favorite-team configuration.
- Web configurator, board emulator, persistent authentication, color controls and Wi-Fi/hotspot recovery.
- Official MLB and configurable RSS/Atom news headlines.
- Clock with timezone dropdown and 12/24-hour formats.
- Open-Meteo and OpenWeatherMap weather adapters, daily forecast high/low, city/state labels and pixel-art icons.
- Shared clock, weather, news and game rotation, with exclusive display priority for live favorite-team games.
- Background weather caching, offline fallback and separately stored OpenWeatherMap credentials.
- Two-pixel safety margins on clock and weather screens.

### Validation
- Raspberry Pi developer reported 550 tests passing (15 skipped) after timezone UI changes.
- Integration review, release tag and deployment verification remain pending.

### Planned
- NBA, NFL, NHL, MLS and EFL modules.
- Further plugin ecosystem and release stabilization.

## Archived release-candidate verification notes (moved from README)

These notes preserve historical candidate observations; some statuses have since changed. Refer to newer entries above for current release acceptance.

## v0.6.0 English football release-candidate verification

- Branch: `feature/0.6.0-english-football`; **not yet merged, tagged or deployed to production**.
- Four divisions: Premier League, Championship, League One and League Two, with ESPN-backed fixtures, scores, club IDs, favorites, shared 64×32 layout and combined live-first rotation.
- English football is disabled by default. Goal enrichment polls ESPN match summaries **only for live fixtures** in the background; failures preserve scores and no network access occurs during frame rendering.
- Historical ESPN summary samples on October 17, 2026 yielded 11/11 stable goal IDs, 11/11 team IDs and match minutes, and 7/11 identified scorers. **Live ESPN goal delivery has not yet been verified**.
- Before production promotion, complete simulated lifecycle acceptance, a full regression run, a live-match observation, and Pi 3 upgrade/rollback health checks. See [v0.6.0 release checklist](docs/V060-RELEASE-CHECKLIST.md).

## v0.5.0 soccer release-candidate verification

- Branch: `feature/0.5.0-soccer`; not yet merged or tagged.
- Raspberry Pi 5 software updater: **1,018 tests, 15 skipped, no failures** (October 17, 2026), as reported from the device.
- MLS and NWSL share a compact 64×32 pixel layout with period/clock, stoppage-time, halftime, goal announcements, favorites, and live-game priority. The browser emulator has been visually reviewed.
- ESPN-style feed parsing and combined-league behavior have automated fixture coverage; real-time provider responses and goal transitions still require live observation.
- Final acceptance: check real MLS and NWSL feed responses and identifiers, both leagues enabled together, no-live supplemental rotation, service restart/health, and physical-matrix appearance where hardware is available. See [v0.5.0 release checklist](docs/V050-SOCCER-RELEASE-CHECKLIST.md).

## v0.4.5 release-candidate verification

- Feature branch: `feature/0.4.5-dashboard-polish`, not yet tagged or merged.
- Raspberry Pi 3: **857 tests passed, 15 skipped** (October 17, 2026), including isolated rollback and fresh-install regression coverage.
- Dashboard update, remote branch discovery, release-family filtering, matrix enable/disable, and rejection of an older unsafe branch confirmed on the Pi 3.
- Raspberry Pi 5: clean Raspberry Pi OS Trixie installation in emulator mode succeeded; board display remained operational after reboot.
- Automated rollback uses isolated command stubs; a real post-deployment failure and restoration have not been demonstrated.
- Remaining acceptance: clean physical-driver install, any outstanding Wi-Fi/operational checks, license review, and release decision.

## v0.4.0 NFL verification

Configure NFL under Sports & Rotation. Enable NFL headlines separately under Content & News. The NFL feed currently targets the local game day, so Sunday's matchups may not appear on Friday. NFL RSS parsing, configuration, and game rendering are covered by regression tests. Live NFL headlines and game transitions still require physical-matrix observation.

## v0.4.0 verification

- Raspberry Pi 3 on Raspberry Pi OS Trixie, 64×32 RGB LED matrix.
- Full regression suite: **780 tests, 15 skipped, no failures** (October 16, 2026).
- Both system services active, with the published framebuffer reported fresh by `ulsctl health`.
- NFL scheduled, live and final rendering, favorites, rotation and automatic news are covered by automated tests. Physical NFL live-game transitions and live RSS headline delivery remain follow-up observations.

## v0.3.0 verification

- Production Raspberry Pi 3 on Raspberry Pi OS Trixie, 64×32 RGB LED matrix.
- Full regression suite: **752 tests, 15 skipped, no failures** (October 16, 2026).
- `uls-web.service` and `uls-matrix.service` enabled and running automatically after reboot.
- Configurator responding on port 8080; physical MLB/NHL and universal news rotation verified previously, with NBA/WNBA display and configuration confirmed for v0.3.0.
- NHL pregame records are visible on the board; NBA/WNBA pregame records appear when available from the feed.
- NHL score feed retains last good data on transient errors and uses the configured timezone for the game-day date.
- NBA/WNBA news controls and RSS parsing are covered by tests; live headline delivery remains to be checked.

