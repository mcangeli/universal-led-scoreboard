# Preview 9: MLB Classic-inspired visual layout

This preview improves score-column alignment, preserves team accents, and renders a compact local start time for scheduled games when the MLB schedule includes `gameDate`. Final, delayed, and postponed states have dedicated bottom labels. Live games retain inning direction, outs and occupied-base indicators.

This is a clean-room **Classic-inspired** renderer, **not** a verified pixel-perfect reproduction of the original MLB-LED-Scoreboard. The original upstream renderer has not yet been fully mapped, and no upstream logos or assets have been copied.

## Test on Raspberry Pi

Stop the previous preview server before running:

```sh
cd ~/universal-led-scoreboard
git pull --ff-only origin feature/0.1.0-core-foundation
python3 -m unittest discover -s tests -v
python3 -m universal_led.preview9 --host 0.0.0.0 --port 8765 --team ATL --mode fallback
```

Visit `http://<pi-ip>:8765` on your trusted LAN. Try `--mode all` to cycle games and `--date YYYY-MM-DD` to preview a particular day's schedule.

Note: `gameDate` is converted using the Pi's local time zone. Set the Pi's time zone correctly. Pregame clock is deliberately compact to fit the native 64x32 matrix. Probable pitchers and logos are still future work. The web preview has no authentication.
