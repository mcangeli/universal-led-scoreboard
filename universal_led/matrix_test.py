"""Safe standalone physical LED panel smoke test; does not start the web server."""
from __future__ import annotations

import argparse
import time

from .display import splash
from .matrix_output import create_matrix, draw_frame


def main():
    parser = argparse.ArgumentParser(description="Display the Universal LED splash on a HUB75 panel")
    parser.add_argument("--mapping", default="adafruit-hat")
    parser.add_argument("--brightness", type=int, default=40)
    parser.add_argument("--gpio-slowdown", type=int, default=2)
    parser.add_argument("--seconds", type=int, default=15)
    args = parser.parse_args()
    if args.seconds < 1 or args.seconds > 300:
        parser.error("--seconds must be between 1 and 300")
    matrix = create_matrix(gpio_mapping=args.mapping, brightness=args.brightness,
                           gpio_slowdown=args.gpio_slowdown)
    print(f"Showing 64x32 splash for {args.seconds} seconds; Ctrl+C to exit.", flush=True)
    try:
        draw_frame(matrix, splash())
        time.sleep(args.seconds)
    except KeyboardInterrupt:
        pass
    finally:
        matrix.Clear()


if __name__ == "__main__":
    main()
