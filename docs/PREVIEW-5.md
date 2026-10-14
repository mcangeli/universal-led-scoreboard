# Preview 5: refined MLB 64x32 offline layout

This preview introduces a **separate** MLBRefinedScreen for visual comparison against Preview 4. It uses the same offline NYM at ATL fixture. This is not yet a faithful reproduction of the original MLB-LED-Scoreboard's Classic design or a live data integration.

The native panel is always 64x32. Team labels use 5x7 glyphs; R/H/E values use a compact 3x5 font. A dedicated bottom strip shows inning/half, outs, and base occupancy during live play. Pregame and final screens show a simple status. Values greater than 99 use a red overflow marker rather than silently showing a misleading score.

Run:

```sh
git pull --ff-only origin feature/0.1.0-core-foundation
python3 -m unittest discover -s tests -v
python3 -m universal_led.preview5 --host 0.0.0.0 --port 8765
```

Stop the prior preview server first. Visit `http://<pi-ip>:8765` from your trusted LAN. This server is unauthenticated, so do not expose it publicly.

Next: compare with upstream 64x32 reference imagery, integrate a real data adapter, and improve logo/color fidelity while retaining strict pixel boundaries.
