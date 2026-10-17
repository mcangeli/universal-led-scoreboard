# Universal LED Scoreboard v0.4.5 release acceptance

Status: feature branch candidate, not merged or tagged.

## Verified on Raspberry Pi 3, Trixie, 64×32 matrix

- [x] Full regression suite: 854 tests passed, 15 skipped (October 17, 2026).
- [x] Dashboard update checks and installations work without shell intervention.
- [x] Dashboard discovers remote branches and offers current release-family filtering.
- [x] Selecting an older incompatible branch produces an unsafe-branch rejection without installing it.
- [x] Physical matrix enable/disable works independently of dashboard and emulator.
- [x] Live games take priority over supplementary screens.

## Remaining release gates

- [ ] Controlled post-checkout failure verifies automatic rollback of code, privileged helpers, dashboard availability, and saved matrix state. Do not inject a failure into the production Pi without a verified recovery image and explicit test procedure.
- [ ] Fresh-image installation in emulator mode, then physical mode on a spare card or Pi; verify password setup, services, board preview, driver, and dashboard update helpers.
- [ ] Verify reboot persistence of matrix configuration and normal dashboard operations.
- [ ] Review redistribution licenses, logos, feeds, and attributions.
- [ ] Run final full regression suite and record count and skipped tests.
- [ ] Merge reviewed candidate into main, then tag v0.4.5. Do not tag or merge before acceptance.

## Fresh-card acceptance procedure

Use a **spare microSD card** on a supported Raspberry Pi. Do not overwrite the working scoreboard image.

1. Flash Raspberry Pi OS Lite **Trixie 64-bit** and configure networking/SSH. Boot as a normal sudo-enabled user.
2. Run the documented v0.4.5 candidate checkout and installer commands in [INSTALLATION.md](INSTALLATION.md), initially with `--mode emulator --branch feature/0.4.5-dashboard-polish`. Record any dependency, permission, or administrator-password error.
3. Confirm that installation finishes, the dashboard responds on port 8080, administrator login works, and **Open Board View** renders a frame.
4. In **System → Software Updates**, verify the installed branch/commit and that **Check for Updates** responds. Confirm Wi-Fi scanning without changing the working network.
5. Reboot the spare-card Pi. Confirm dashboard login and board preview still work. Use `sudo ulsctl health` and `sudo ulsctl status` only for troubleshooting.
6. For physical validation, use a **separate clean card** installed with `--mode physical` and the same branch, with correct HUB75 wiring and independent matrix power. Confirm matrix service, startup splash, saved brightness/mapping, enabled/disabled state across reboot, and dashboard update availability.
7. Preserve a copy of test logs with secrets redacted. Record the tested Pi model, OS image, and pass/fail results before marking this gate complete.

A successful upgrade of an existing installation is **not** a substitute for this test. No fresh-card validation has been reported yet.

## Safe downgrade policy

The dashboard intentionally rejects older or divergent Git histories. Branch discovery does not imply deployability. For disaster recovery, restore a known-good image or perform an explicitly supervised recovery rather than forcing an older checkout through the dashboard.

## Maintenance

Use **System → Software Updates** for routine updates and branch selection, and **System → Matrix Hardware** for physical output. Shell commands are recovery-only after the initial installation. Configuration remains in /etc/uls and persistent state in /var/lib/uls.

## Previously released versions

Historical v0.1.0 foundation checks have been superseded by this checklist. See CHANGELOG.md for v0.2.0 through v0.4.5 development history.
