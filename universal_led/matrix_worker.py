"""Read-only physical matrix worker; never handles web authentication."""
from __future__ import annotations
import argparse
from pathlib import Path
import signal
import time
from .display import splash
from .frame_bridge import read_frame
from .matrix_output import create_matrix, draw_frame
from .matrix_settings import load_matrix_settings

def main():
    parser = argparse.ArgumentParser(description="Physical 64x32 scoreboard worker")
    parser.add_argument("--frame-file", type=Path, default=Path("/run/uls/live-frame.ppm"))
    parser.add_argument("--mapping", default="adafruit-hat")
    parser.add_argument("--brightness", type=int, default=40)
    parser.add_argument("--gpio-slowdown", type=int, default=4)
    parser.add_argument("--interval", type=float, default=0.2)
    parser.add_argument("--config-file", type=Path, default=Path("/etc/uls/matrix.json"))
    args = parser.parse_args()
    if not 0.05 <= args.interval <= 10:
        parser.error("--interval must be between 0.05 and 10 seconds")
    try:
        settings = load_matrix_settings(args.config_file)
    except (ValueError, OSError) as exc:
        parser.error(f"Invalid matrix configuration: {exc}")
    # Preserve the deployed service arguments until a matrix.json exists.
    # Once saved, the dashboard configuration becomes authoritative.
    if args.config_file.exists():
        mapping = settings["mapping"]
        brightness = settings["brightness"]
        slowdown = settings["gpio_slowdown"]
        interval = settings["interval"]
        if not settings["enabled"]:
            print("Physical matrix disabled in configuration.", flush=True)
            return
    else:
        mapping, brightness, slowdown, interval = (
            args.mapping, args.brightness, args.gpio_slowdown, args.interval
        )
    matrix = create_matrix(gpio_mapping=mapping, brightness=brightness,
                           gpio_slowdown=slowdown)
    running = True
    def stop(_signal, _frame):
        nonlocal running
        running = False
    signal.signal(signal.SIGTERM, stop)
    signal.signal(signal.SIGINT, stop)
    canvas = matrix.CreateFrameCanvas()
    last_mtime = None
    try:
        # Fixed startup splash on every physical worker start, independent of feeds.
        canvas = draw_frame(matrix, splash(matrix.width, matrix.height), canvas=canvas)
        deadline = time.monotonic() + 30.0
        while running and time.monotonic() < deadline:
            time.sleep(min(0.2, max(0.0, deadline - time.monotonic())))
        if not running:
            return
        while running:
            try:
                stat = args.frame_file.stat()
                if stat.st_mtime_ns != last_mtime:
                    frame = read_frame(args.frame_file)
                    canvas = draw_frame(matrix, frame, canvas=canvas)
                    last_mtime = stat.st_mtime_ns
            except (FileNotFoundError, ValueError, OSError) as exc:
                print(f"Frame unavailable: {exc}", flush=True) if last_mtime is None else None
            time.sleep(interval)
    finally:
        matrix.Clear()

if __name__ == "__main__":
    main()
