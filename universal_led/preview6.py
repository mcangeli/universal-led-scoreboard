"""Live MLB API browser preview, native 64x32. Requires network access."""
import argparse
import time
from .display import splash
from .mlb_data import MLBFeed
from .mlb_refined import MLBRefinedScreen
from .web_preview import serve

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--host', default='127.0.0.1')
    parser.add_argument('--port', type=int, default=8765)
    parser.add_argument('--team', default='ATL',
                        help='Three-letter abbreviation, or ALL for all games')
    parser.add_argument('--date', default=None, help='YYYY-MM-DD, default Pi local date')
    parser.add_argument('--refresh', type=float, default=60)
    parser.add_argument('--seconds', type=float, default=12)
    args = parser.parse_args()
    if args.seconds <= 0:
        parser.error('--seconds must be positive')
    feed = MLBFeed(team=None if args.team.upper() == 'ALL' else args.team,
                   date=args.date, refresh_seconds=args.refresh)
    started = time.monotonic()
    def frame():
        games = feed.games()
        if not games:
            return splash()
        index = int((time.monotonic()-started)//args.seconds)%len(games)
        return MLBRefinedScreen(games[index]).render()
    print('MLB API preview: no games or unavailable data => splash screen',flush=True)
    serve(host=args.host,port=args.port,frame_provider=frame)

if __name__ == '__main__':
    main()
