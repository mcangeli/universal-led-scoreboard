# Preview 14: native dashboard and MLB sport settings

The configurator now includes Dashboard, Sports, Colors and System navigation.
The MLB Sports page saves a favorite team, game-selection mode, rotation
duration and MLB feed refresh interval. Settings are versioned and stored in
`~/.config/universal-led-scoreboard/settings.json` using atomic writes and
timestamped backups.

MLB is the only active renderer. NBA, NFL, NHL, MLS and EFL remain planned,
and cannot be selected as active sports until implemented.

Saving Sports settings applies the favorite team and rotation mode to the
configurator's current MLB game selection. Refresh timing is updated in the
background feed. The separate Preview 11 process does **not** receive these
settings automatically; direct integration with the final engine remains future work.

## Test on Raspberry Pi

Stop the old configurator, then:

```sh
cd ~/universal-led-scoreboard
git pull --ff-only origin feature/0.1.0-core-foundation
python3 -m unittest discover -s tests -v
python3 -m universal_led.configurator --port 8080
```

Open `http://YOUR_PI_IP:8080` on your trusted LAN.

Visit Sports, change the favorite MLB team and rotation settings, save,
then refresh the page and confirm persistence. Colors should continue to
function as before. System currently shows a placeholder; it does not
manage hardware or systemd services yet.

This preview has no login authentication and must not be internet-exposed.
