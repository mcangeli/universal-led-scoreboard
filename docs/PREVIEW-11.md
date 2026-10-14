# Preview 11: full color roles on the MLB display

Preview 11 uses the shared palette for every primary MLB scoreboard element:
- `text`: R/H/E numeric values and default team labels
- `dim`: unoccupied bases and unlit outs
- `accent`: R/H/E headers, inning, base runners, scheduled/final labels
- `error`: recorded outs, overflow markers, delayed/postponed labels
- `separator`: horizontal separator line

Team abbreviation colors remain independently overridable.

## Raspberry Pi test

Stop the previous preview first.

```sh
cd ~/universal-led-scoreboard
git pull --ff-only origin feature/0.1.0-core-foundation
python3 -m unittest discover -s tests -v
python3 -m universal_led.preview11 --host 0.0.0.0 --port 8765 --team ATL --mode fallback
```

To test global colors, create `my-scoreboard.json`:

```json
{"accent":"#00FF00","error":"#FF00FF","separator":"#223344"}
```

Then add `--scoreboard-colors my-scoreboard.json` to the command.

The colors load on startup; restart the preview to apply edits. The preview is LAN-only and unauthenticated.

The original MLB-LED-Scoreboard color file schema has not been verified. Native compatibility/import is a separate upcoming task.
