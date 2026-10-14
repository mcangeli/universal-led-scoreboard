# Preview 18: Raspberry Pi diagnostics

The **System** tab now shows read-only information from the host:
device model, hostname, OS/kernel, Python version, CPU temperature when
available, host uptime, free disk space, current backend, and systemd
user-service state and enabled status.

The endpoint is `GET /api/system`. All subprocess calls have a two-second
timeout and fixed arguments. The service status is queried read-only.

**No remote restart/stop controls are exposed yet.** The configurator is
accessible on the trusted LAN without user authentication, so adding
state-changing system controls would be unsafe until authentication and
authorization are implemented. No HUB75 panel is connected; its status
is reported as not configured rather than pretending to detect hardware.

## Update and test

```sh
cd ~/universal-led-scoreboard
git pull --ff-only origin feature/0.1.0-core-foundation
python3 -m unittest discover -s tests -v
systemctl --user restart universal-led-scoreboard
```

Open `http://PI_IP:8080/`, select **System**, and verify the
model, temperature, free space, and user-service state. The Board View
and all existing settings should remain functional.
