# v0.1.0 Core Foundation release gate

Status: candidate, not tagged. Validate on a real Pi before merging or tagging.

## What is implemented

- MLB live, pregame, final, favorite-team selection and 64x32 rotation.
- Shared countdown renderer; automatic MLB league and favorite-team opening dates.
- Background opening-day schedule fetch, cache fallback, and diagnostics.
- Native configurator, protected settings, board emulator, Wi-Fi tools.
- Clock, weather, news, system services, and physical matrix startup splash.

NBA, NFL, NHL, MLS, and EFL data/rendering remain future releases. Their countdown layout can reuse the shared renderer.

## Deployed system layout

- Application: `/opt/uls/app`
- Virtual environment: `/opt/uls/venv`
- Settings and credentials: `/etc/uls`
- Persistent data: `/var/lib/uls`
- Published frame: `/run/uls/live-frame.ppm`
- Services: `uls-web.service`, `uls-matrix.service`
- Dashboard: `http://<pi-host>:8080/`

The older `universal-led-scoreboard.service` user service and `scripts/install.sh` are legacy preview paths. Do not run them over an existing `/opt/uls` system installation.

## Upgrade and smoke test

```bash
sudo ulsctl update
sudo ulsctl status
sudo ulsctl health
```

Updater must run all unit tests successfully before applying the fast-forward, restart both system services, and preserve settings and persistent data. After the physical startup splash (30 seconds), the board must resume live frames.

## Manual release checks

- [ ] Restart from dashboard: both services restart, startup splash displays, normal frames resume.
- [ ] Run `sudo ulsctl restart` and confirm the same behavior.
- [ ] Run `sudo ulsctl health` after the splash: both services active, HTTP health responds, frame fresh.
- [ ] Disable or disconnect network temporarily: web UI stays responsive and cached content continues where available.
- [ ] Confirm MLB schedule failure never blocks frame generation; diagnostics report the warning.
- [ ] Confirm countdown league and ATL favorite-team dates; ensure countdown yields to live game.
- [ ] Confirm clock, weather, news, and game screens rotate without empty slots.
- [ ] Confirm saving settings survives web service restart without invalid form token.
- [ ] Verify Wi-Fi recovery/fallback using the existing Wi-Fi deployment checklist.
- [ ] Validate a clean installation on a supported Pi using documented system-service steps.
- [ ] Review GPL and third-party attribution before public release.

## Recovery

```bash
sudo ulsctl status
sudo ulsctl logs
sudo ulsctl restart
sudo ulsctl health
```

If the dashboard restart control is unavailable on a migrated system, install its scoped helper once:

```bash
sudo bash /opt/uls/app/scripts/install-dashboard-restart-helper.sh
```

The updater rejects dirty working trees and failed candidate tests; if service validation fails after applying code, it attempts rollback to the prior commit.

## Release decision

Only merge and tag `v0.1.0` after the test suite and manual checks are recorded as passing. Do not tag solely because unit tests pass.
