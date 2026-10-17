# Changelog

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
- Raspberry Pi 3: 854 regression tests passed, 15 skipped, before final documentation/version changes.
- Web updates, branch discovery, and matrix on/off controls verified on physical hardware.
- Pending: incompatible-branch rejection in browser, simulated post-checkout rollback, fresh-image installation, and release tagging. No merge to main yet.


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
