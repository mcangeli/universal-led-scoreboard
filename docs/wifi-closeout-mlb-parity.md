# Finish Wi-Fi, then restore upstream MLB 64×32 fidelity

## Sources verified
- Existing configurator: https://github.com/mcangeli/mlb-scoreboard-configurator/blob/main/mlb_scoreboard_configurator/network.py
- Original scoreboard: https://github.com/MLB-LED-Scoreboard/mlb-led-scoreboard
- Original renderer dispatch: renderers/main.py
- Universal current MLB renderer: universal_led/mlb_classic.py

## Wi-Fi: reuse instead of redesign
The existing MLB configurator has status(), scan(), connect(), disconnect(),
start_hotspot(), stop_hotspot(), and maintain_hotspot() built around nmcli.
Universal already has read-only diagnostics and scanning plus a tested root
rollback worker. Reuse the original behavior and UI, not the original command
execution verbatim: the original connect() passes passwords as process argv,
which can expose credentials. The original scan() also uses simple colon
splitting; Universal already has escaped-field parsing tests.

Minimum completion criteria:
1. A scoped privileged connection operation, not unrestricted web-server sudo.
2. Network scan, saved profile handling, connect, status, hotspot fallback.
3. Recovery armed before switching; confirmation only when connection verified.
4. Successful and unsuccessful connection test with independent Ethernet access.
5. Connect enabled after those tests, no more architecture previews.

## MLB display: visual parity before additional sports
The current MLBClassicScreen is documented as a clean-room inspired layout;
it does not replicate upstream renderers. Compare the original upstream
renderers/games/{game,pregame,postgame}.py, coordinate layouts, font assets,
and color configuration to the current 64×32 framebuffer. Preserve original
appearance where license permits and attribute reused material.

Acceptance fixtures:
- Pregame with scheduled start time
- Live game: top/bottom inning, outs, base occupancy, R/H/E
- Double-digit runs and hits
- Final game, including extra innings
- Braves favorite team and all-games rotation
- Actual 64×32 emulator screenshot comparisons

Once Wi-Fi is done, MLB parity is the next milestone. NBA follows MLB parity.

## Development Pi hotspot: verified manual test (2026-10-15)

The development Raspberry Pi has a NetworkManager access-point profile:

- Profile name and SSID: `Universal-LED-Setup`
- Password on this **specific development Pi**: `ScoreBoard` (case-sensitive)
- Wireless interface: `wlan0`
- Security: WPA-PSK; wireless mode: AP; IPv4 method: shared
- Autoconnect: disabled, so activating the hotspot is explicit
- Manual activation through the scoped Wi-Fi control helper was successful; a client connected.
- Ethernet `eth0` remained available for management during testing.

**Do not treat `ScoreBoard` as an application-wide or production default.** It is
currently a known development-device credential, not a password provisioned
by the Universal installer. For production, generate a distinct per-device
hotspot password, show it locally to the owner during setup, and allow it to
be changed. Never log or expose hotspot passwords in the web status API.

The hotspot helper currently toggles a pre-existing profile; it does not yet
provision a profile on a fresh install or automatically activate a fallback.
Those features and an end-to-end recovery test remain required.

## Hotspot password setup and admin management (approved requirement)

- During installation, create a dedicated `Universal-LED-Setup` NetworkManager AP profile, with `connection.autoconnect=no`, WPA-PSK and IPv4 shared mode. Do not overwrite `mlb-scoreboard-setup`.
- Offer a memorable generated password (e.g. three short words plus two digits, minimum 8 characters), or allow a custom password of 8–63 bytes. Do not mandate arbitrary uppercase/symbol complexity.
- Display the chosen password to the installer once, with instructions to store it. Never embed a common password such as `ScoreBoard` as a production default.
- Under authenticated System → Wi-Fi → Hotspot Settings, allow an administrator to set a replacement password and, optionally, change the SSID. Require confirmation of the new password. Do not expose the old password in HTML, JSON, logs, shell arguments, or diagnostic output.
- Write secrets through a narrowly privileged, root-owned helper. Avoid `nmcli connection modify ... psk PASSWORD` because that leaks the password into process arguments. Validate length and reject control characters.
- Update the saved profile without immediately restarting an active hotspot. Warn that clients must reconnect after the next activation. Do not interrupt the active management connection.
- Test fresh-install provisioning, password update, bad-password rejection, permission checks, no-secret logging, and connection persistence on Raspberry Pi Bookworm/Trixie before enabling this UI.

## Final Wi-Fi closeout implementation (requires live Pi validation)

- `sudo python3 scripts/provision-wifi-hotspot.py` creates the dedicated AP with a
  per-device generated password or a custom one. It retains an existing AP unchanged.
  The chosen password is displayed once in the interactive installer session.
- `sudo bash scripts/install-wifi-hotspot-maintenance.sh` installs a root-owned
  maintenance worker and enables its systemd timer. It checks every two minutes.
- A healthy client connection is never disturbed. An active hotspot is also
  preserved so management sessions are not interrupted.
- With no active Wi-Fi connection, the worker tries saved client profiles and
  activates Universal-LED-Setup if none succeeds. It will not operate during
  a pending recovery rollback.
- **Limit:** While the AP is active, this worker does not periodically interrupt
  it to retry client networks. Returning to client Wi-Fi is currently manual
  through the Wi-Fi tab. Full non-disruptive AP-to-client automatic recovery
  needs additional validation/design, and must not be claimed complete.
- Run the full regression suite and live-test on Raspberry Pi before production
  deployment. The password editor and new AP provisioning are not yet live verified.
