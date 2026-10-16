"""Read-only physical matrix worker; never handles web authentication."""
from __future__ import annotations
import argparse
from pathlib import Path
import signal
import time
from .frame_bridge import read_frame
from .matrix_output import create_matrix, draw_frame

def main():
    parser = argparse.ArgumentParser(description="Physical 64x32 scoreboard worker")
    parser.add_argument("--frame-file", type=Path, default=Path("/run/uls/live-frame.ppm"))
    parser.add_argument("--mapping", default="adafruit-hat")
    parser.add_argument("--brightness", type=int, default=40)
    parser.add_argument("--gpio-slowdown", type=int, default=4)
    parser.add_argument("--interval", type=float, default=0.2)
    args = parser.parse_args()
    if not 0.05 <= args.interval <= 10:
        parser.error("--interval must be between 0.05 and 10 seconds")
    matrix = create_matrix(gpio_mapping=args.mapping, brightness=args.brightness,
                           gpio_slowdown=args.gpio_slowdown)
    running = True
    def stop(_signal, _frame):
        nonlocal running
        running = False
    signal.signal(signal.SIGTERM, stop)
    signal.signal(signal.SIGINT, stop)
    last_mtime = None
    try:
        while running:
            try:
                stat = args.frame_file.stat()
                if stat.st_mtime_ns != last_mtime:
                    frame = read_frame(args.frame_file)
                    draw_frame(matrix, frame)
                    last_mtime = stat.st_mtime_ns
            except (FileNotFoundError, ValueError, OSError) as exc:
                print(f"Frame unavailable: {exc}", flush=True) if last_mtime is None else None
            time.sleep(args.interval)
    finally:
        matrix.Clear()

if __name__ == "__main__":
    main()
