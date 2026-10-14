# Preview 21.2: Persistent administrator sessions

Administrator sessions now survive browser refreshes and configurator service
restarts for up to eight hours after login. Session identifiers are random,
stored in an HttpOnly SameSite=Strict browser cookie, and stored **only as
SHA-256 hashes** in `sessions.sqlite3` under the application's config directory
(mode 0600). Signing out revokes the token in persistent storage. Changing
the administrator password invalidates all previously issued sessions.

Sessions created before this update were held only in memory and cannot be
migrated. **One new login after updating is expected.** Later refreshes and
restarts should preserve that session until it expires.

This does not encrypt HTTP. Keep the configurator on a trusted LAN or put
it behind HTTPS before exposing it to untrusted networks.

## Verify on Pi

```sh
cd ~/universal-led-scoreboard
git pull --ff-only origin feature/0.1.0-core-foundation
python3 -m unittest discover -s tests -v
systemctl --user restart universal-led-scoreboard
```

Log in once, refresh the browser, restart the user service, then refresh again.
Both refreshes should keep the user signed in.
