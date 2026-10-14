# Preview 10: configurable team and scoreboard colors

Adds a reusable color loader, default MLB team palette, and JSON override files.
Overrides are loaded at startup and do not modify repository defaults.

**Compatibility note:** This preview does not claim complete compatibility with the
original MLB-LED-Scoreboard `colors/teams.json` or `colors/scoreboard.json`.
Its supported JSON override formats are documented below. Original-file schema
mapping and import tools will follow after upstream formats are verified.

## Examples

Create `my-teams.json`:
```json
{
  "ATL": {"primary": "#CE2036"},
  "NYM": [245, 128, 38]
}
```

Create `my-scoreboard.json`:
```json
{
  "text": "#EBEBE1",
  "dim": [110,125,140],
  "accent": "#EFC35F",
  "error": "#F05046",
  "separator": [28,37,48]
}
```

Run on Pi (stop the previous preview first):

```sh
cd ~/universal-led-scoreboard
git pull --ff-only origin feature/0.1.0-core-foundation
python3 -m unittest discover -s tests -v
python3 -m universal_led.preview10 --host 0.0.0.0 --port 8765 --team ATL --mode fallback --team-colors my-teams.json --scoreboard-colors my-scoreboard.json
```

For a quick check without custom files, omit the two `--*-colors` arguments.

Future work: extract and validate the original upstream color schemas, add an importer,
integrate all scoreboard color roles (including status/score/outs), and expose color
selection in the web configurator. Preview is LAN-only and unauthenticated.
