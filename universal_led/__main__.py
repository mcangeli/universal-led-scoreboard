"""Generate a startup splash preview without Raspberry Pi hardware."""
import argparse
from pathlib import Path
from .display import splash

def main():
    parser = argparse.ArgumentParser(description='Universal LED Scoreboard preview')
    parser.add_argument('--output', type=Path, default=Path('splash.ppm'))
    args = parser.parse_args()
    args.output.write_bytes(splash().ppm())
    print(f'Wrote 64x32 splash preview: {args.output}')

if __name__ == '__main__':
    main()
