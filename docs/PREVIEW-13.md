# Preview 13: interactive color editor improvements

Adds to the native configurator:
- Immediate 64x32 preview of unsaved changes
- Unsaved-changes indicator
- Cancel Changes to restore the last loaded/saved palette
- Reset Selected Color to the built-in default (select/focus a color control first)
- Preview favorite team selection, including when the team has no game

## Raspberry Pi

Stop the previous configurator, then:

```sh
cd ~/universal-led-scoreboard
git pull --ff-only origin feature/0.1.0-core-foundation
python3 -m unittest discover -s tests -v
python3 -m universal_led.configurator --port 8080
```

Open `http://YOUR_PI_IP:8080` on your trusted LAN.

Try selecting ATL in the preview-team menu and changing ATL's color.
The simulated matrix should update immediately, even without a Braves game.
Try Cancel, then change and Reset Selected Color. Finally save, restart the
configurator, and confirm the saved colors persist.

This preview focuses on color-editor ergonomics. The dashboard, sport settings,
rotation controls, and direct running-engine updates remain upcoming work.
The service has no user authentication and must not be exposed to untrusted
networks or the Internet.
