"""Live MLB visual preview, native 64x32."""
import argparse
import time
from .display import splash
from .mlb_data import MLBFeed
from .mlb_runtime import BackgroundMLBFeed, select_games
from .mlb_visual import MLBVisualScreen
from .web_preview import serve

def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('--host',default='127.0.0.1')
    parser.add_argument('--port',type=int,default=8765)
    parser.add_argument('--team',default='ATL')
    parser.add_argument('--mode',choices=('favorite','fallback','all'),default='fallback')
    parser.add_argument('--date',default=None)
    parser.add_argument('--refresh',type=float,default=60)
    parser.add_argument('--seconds',type=float,default=12)
    args=parser.parse_args()
    if args.seconds<=0 or args.refresh<=0:
        parser.error('refresh and seconds must be positive')
    worker=BackgroundMLBFeed(MLBFeed(team=None,date=args.date,refresh_seconds=args.refresh))
    worker.start()
    started=time.monotonic()
    def frame():
        games=select_games(worker.games(),args.team,args.mode)
        if not games: return splash()
        game=games[int((time.monotonic()-started)//args.seconds)%len(games)]
        return MLBVisualScreen(game).render()
    try:
        serve(host=args.host,port=args.port,frame_provider=frame)
    finally:
        worker.stop()
if __name__=='__main__':
    main()
