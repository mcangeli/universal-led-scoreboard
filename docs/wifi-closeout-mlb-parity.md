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
