# Preview 19: Administrator login foundation

Preview 19 introduces a mandatory administrator password for the native
configurator **and** board emulator. Existing configuration, live MLB feed,
color editor, dashboard, and system diagnostics remain available after login.

Security features:
- Password stored using salted PBKDF2-HMAC-SHA256 (600,000 iterations)
- Password set interactively, never placed in shell history or unit files
- Random eight-hour in-memory session cookies (HttpOnly, SameSite=Strict)
- Login, logout, and access checks for UI and data endpoints
- Existing anti-CSRF request token retained for configuration writes
- Existing sessions are invalidated when the service restarts

**Important:** This is an authentication foundation for a trusted LAN,
not an Internet-facing security solution. HTTP is not encrypted; passwords
and cookies can be intercepted on an untrusted network. HTTPS, stronger
login throttling, and robust browser origin checks must precede exposure
beyond a trusted LAN. Remote restart/stop buttons are deliberately deferred
until those protections and a safe out-of-process service controller exist.

## Update Raspberry Pi (important: set password before restart)

```sh
cd ~/universal-led-scoreboard
git pull --ff-only origin feature/0.1.0-core-foundation
python3 -m unittest discover -s tests -v
python3 -m universal_led.configurator --set-admin-password
systemctl --user restart universal-led-scoreboard
systemctl --user status universal-led-scoreboard
```

Open `http://PI_IP:8080/`. You should be redirected to the
administrator login. Verify that `/board` also requires login, then
sign in, test settings and colors, and use **Sign Out**.

If the password is forgotten, run the `--set-admin-password` command
again on the Pi and restart the service. Never forward port 8080 to
the public Internet.
