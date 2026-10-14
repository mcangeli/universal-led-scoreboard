# Preview 4: 64x32 MLB Classic prototype

**Status:** Initial original implementation inspired by MLB LED Scoreboard; **not yet a faithful upstream renderer port**. No logos, fonts, game feeds, or code have been copied from upstream.

## Layout and constraints

- Native 64x32 RGB framebuffer; all elements use fixed integer pixel coordinates.
- Three-letter away/home abbreviations, runs/hits/errors, inning, outs and base occupancy.
- Pregame, live and final states; two-digit runs are supported in the compact score grid.
- No hardware or network dependencies. Data is a clearly labeled offline fixture.
- Game stats above 99 are temporarily capped in the rendering; revisit for production.
- 64x32 is the primary design constraint for **all** future league renderers.

## Pi 5 emulator test

Stop the existing emulator first.

```sh
git pull --ff-only origin feature/0.1.0-core-foundation
python3 -m unittest discover -s tests -v
python3 -m universal_led.preview4 --host 0.0.0.0 --port 8765
```

Open `http://<pi-ip>:8765` on a trusted LAN. The splash appears for 3 seconds, then the MLB prototype and splash alternate every 12 seconds. No authentication is present: do not expose port 8765 publicly.

## Next work

Review visual parity against upstream 64x32 screenshots and existing renderer code, choose properly licensed assets/fonts, then build the MLB Stats API adapter with caching and error recovery. Do not describe this prototype as live MLB or exact upstream Classic parity.
