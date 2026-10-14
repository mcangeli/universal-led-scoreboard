"""Preview 7: background MLB updates and favorite-team fallback."""
import argparse
import time
from .display import splash
from .mlb_data import MLBFeed
from .mlb_runtime import BackgroundMLBFeed, select_games
from .mlb_refined import MLBRefinedScreen
from .web_preview import serve

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--host', default='127.0.0.1')
    parser.add_argument('--port', type=int, default=8765)
    parser.add_argument('--team', default='ATL', help='Preferred team abbreviation')
    parser.add_argument('--mode', choices=('favorite','fallback','all'), default='fallback')
    parser.add_argument('--date', default=None, help='YYYY-MM-DD')
    parser.add_argument('--refresh', type=float, default=60)
    parser.add_argument('--seconds', type=float, default=12)
    args = parser.parse_args()
    if args.seconds <= 0 or args.refresh <= 0:
        parser.error('--seconds and --refresh must be positive')
    # Fetch all games, then select locally; enables fallback without a second API request.
    worker = BackgroundMLBFeed(MLBFeed(team=None, date=args.date,
                                      refresh_seconds=args.refresh))
    worker.start()
    started = time.monotonic()
    def frame():
        games = select_games(worker.games(), args.team, args.mode)
        if not games:
            return splash()
        index = int((time.monotonic()-started)//args.seconds)%len(games)
        return MLBRefinedScreen(games[index]).render()
    try:
        print('Preview 7: background MLB feed; selection mode:',args.mode,flush=True)
        serve(host=args.host,port=args.port,frame_provider=frame)
    finally:
        worker.stop()

if __name__ == '__main__':
    main()
