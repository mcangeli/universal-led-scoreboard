# Preview 20: Wi-Fi visibility and service groundwork

The System page now includes **read-only NetworkManager Wi-Fi diagnostics**
and a refresh button. This prepares for secure Wi-Fi onboarding without
modifying an active network connection. The endpoint `GET /api/wifi` returns
Wi-Fi radio state, device state, and active connection name. It does not
return passwords, connection profiles, or BSSIDs. If `nmcli` is unavailable,
the interface displays an unavailable state rather than failing.

The existing user systemd service state remains visible in System.

## Upcoming Wi-Fi onboarding architecture

1. Detect whether NetworkManager and a supported wireless interface exist.
2. Detect first-boot/no-network condition and start a temporary setup AP.
3. Serve a mobile-friendly provisioning page over the setup network.
4. Scan SSIDs and collect credentials without storing them in app settings.
5. Apply credentials through NetworkManager with a narrowly scoped privileged
   helper, validate connectivity, then stop the AP only after success.
6. Recover the AP on failure, preserve known-good networks, and avoid
   disrupting an established connection.

Do **not** automatically create a hotspot on existing devices yet.
Onboarding needs a safe privilege boundary, recovery tests, and careful
handling of Pi Wi-Fi radio capabilities.

## Raspberry Pi update

```sh
cd ~/universal-led-scoreboard
git pull --ff-only origin feature/0.1.0-core-foundation
python3 -m unittest discover -s tests -v
systemctl --user restart universal-led-scoreboard
```

Open **System** and refresh Wi-Fi status. No network settings will be changed.
