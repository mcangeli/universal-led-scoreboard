# Preview 21.3: Wi-Fi setup selection and safety checks

The System page now allows selecting a scanned network and shows its security
type and password input. **Connect is deliberately disabled** while the
privilege-restricted NetworkManager helper and rollback mechanism are built.
The password is not sent or stored by this preview.

The new `wifi_provisioning` module validates SSID length, security types,
and password format. It also exposes a readiness policy that refuses to
modify the network until recovery mechanisms are in place.

## Verify

```sh
cd ~/universal-led-scoreboard
git pull --ff-only origin feature/0.1.0-core-foundation
python3 -m unittest discover -s tests -v
systemctl --user restart universal-led-scoreboard
```

Log in, open **System**, scan, and click **Select** next to a network.
Its name and security should appear below the scan results. Connecting is
not yet possible, and the existing Wi-Fi connection must remain intact.
