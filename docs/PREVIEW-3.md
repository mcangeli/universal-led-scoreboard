# Preview 3: screen rotation and MLB offline demo

This preview introduces a small screen plugin protocol, a deterministic offline baseball fixture, and a time-based engine that displays the startup splash then rotates through enabled screens.

**This is not yet MLB Classic or a live scores integration.** The first baseball screen is an intentionally simple demonstration for testing layout and rotation. The original MLB project's visual style will be addressed during the proper renderer integration.

## Run on the Pi 5

```sh
git pull --ff-only origin feature/0.1.0-core-foundation
python3 -m unittest discover -s tests -v
python3 -m universal_led.preview3 --host 0.0.0.0 --port 8765 --seconds 8
```

Visit `http://<pi-ip>:8765` from a trusted LAN browser. Stop the old Preview 2 server first so port 8765 is free. The startup splash displays for 3 seconds, followed by an offline MLB demo for 8 seconds and another splash screen for 8 seconds, repeating.

The preview endpoint has no authentication. Do not expose it to the internet.

## Architecture notes

- A screen implements `name` and `render() -> Framebuffer`.
- `ScoreboardEngine` chooses a screen using an injected monotonic clock, which makes rotation testable.
- Future screens will use a separate data adapter and preserve each league's Classic appearance.
- The rotation engine is currently a preview-only component; persistent configuration and fault isolation are upcoming work.
