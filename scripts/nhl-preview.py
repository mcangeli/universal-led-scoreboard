#!/usr/bin/env python3
"""Write offline NHL visual samples as PPM files for pixel-perfect inspection."""
from pathlib import Path
import argparse
from universal_led.nhl_data import parse_game
from universal_led.nhl_visual import NHLVisualScreen


def sample(state: str):
    payload = {
        "id": 1,
        "startTimeUTC": "2026-10-16T23:00:00Z",
        "gameState": state,
        "awayTeam": {"abbrev": "BOS", "score": 2},
        "homeTeam": {"abbrev": "NYR", "score": 3},
        "periodDescriptor": {"number": 3, "periodType": "REG"},
        "clock": {"timeRemaining": "04:32"},
    }
    if state == "FUT":
        payload["awayTeam"].pop("score")
        payload["homeTeam"].pop("score")
    if state == "OT":
        payload["gameState"] = "LIVE"
        payload["periodDescriptor"] = {"number": 4, "periodType": "OT"}
    if state == "SO":
        payload["gameState"] = "FINAL"
        payload["periodDescriptor"] = {"number": 5, "periodType": "SO"}
    return parse_game(payload)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--output-dir", default="/tmp/uls-nhl-preview")
    args = parser.parse_args()
    output = Path(args.output_dir)
    output.mkdir(parents=True, exist_ok=True)
    for name, state in (("pregame", "FUT"), ("live", "LIVE"),
                        ("overtime", "OT"), ("shootout", "SO"),
                        ("final", "FINAL"), ("postponed", "PPD")):
        path = output / f"nhl-{name}.ppm"
        path.write_bytes(NHLVisualScreen(sample(state)).render().ppm())
        print(path)
    path = output / "nhl-no-games.ppm"
    path.write_bytes(NHLVisualScreen().render().ppm())
    print(path)


if __name__ == "__main__":
    main()
