# Preview 6: live MLB Stats API adapter

This preview adds a network-backed data adapter, without modifying the 64x32 renderer. The MLB Stats API is queried using the schedule endpoint hydrated with linescore data. It includes scores, R/H/E, inning, outs and base occupancy when the API provides those fields.

## Run on Raspberry Pi

Stop the previous preview server before starting:

```sh
git pull --ff-only origin feature/0.1.0-core-foundation
python3 -m unittest discover -s tests -v
python3 -m universal_led.preview6 --host 0.0.0.0 --port 8765 --team ATL
```

Open `http://<pi-ip>:8765` on your LAN. The preview requests the current local date on the Pi. To rotate all MLB games that day:

```sh
python3 -m universal_led.preview6 --host 0.0.0.0 --port 8765 --team ALL
```

Use `--date YYYY-MM-DD` for a specific day, `--refresh 60` to change the polling interval, and `--seconds 12` to change the per-game rotation interval.

If there are no games for the selected team/date, or the initial API request fails, the splash is shown. After a later failure, the last successfully fetched game data is retained. No fabricated live game is displayed.

## Limitations

- MLB team abbreviations rely on schedule API metadata, with a first-three-letter fallback; some team names may require a mapping.
- The current browser handler performs a synchronous network refresh on a request when the cache expires (8-second HTTP timeout); background refresh will be added later.
- The browser preview is read-only and unauthenticated: **LAN only**.
- Pregame and final presentation is still minimal; MLB Classic visual parity, team colors, logos, postponed/delayed status, and a proper setup/configuration UI are future work.
- Stats API data and schedules can change; this is a preview, not a production release.
