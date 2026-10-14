# Preview 21: Wi-Fi network discovery

This first Preview 21 increment adds authenticated Wi-Fi scanning to the
System page. Click **Scan Networks** to list nearby SSIDs, signal percentages,
security types, and the currently connected network. The backend uses
NetworkManager's `nmcli` with a bounded subprocess timeout and returns
only scan metadata, never saved network passwords.

Scanning is read-only. **Connecting to a network and hotspot fallback are
not enabled in this increment.** A narrowly scoped privilege boundary,
network recovery, and safe handling of remote disconnection must come first.

## Raspberry Pi verification

```sh
cd ~/universal-led-scoreboard
git pull --ff-only origin feature/0.1.0-core-foundation
python3 -m unittest discover -s tests -v
systemctl --user restart universal-led-scoreboard
```

Log in at `http://PI_IP:8080/`, open **System**, click **Scan Networks**,
and verify the nearby networks appear. Your existing connection should
remain unchanged.
