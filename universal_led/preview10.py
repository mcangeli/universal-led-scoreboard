"""Preview 10: configurable team and scoreboard colors."""
import argparse
import time
from .display import splash
from .mlb_data import MLBFeed
from .mlb_runtime import BackgroundMLBFeed,select_games
from .mlb_colored import MLBColoredScreen
from .colors import load_palette
from .web_preview import serve

def main():
    p=argparse.ArgumentParser()
    p.add_argument('--host',default='127.0.0.1')
    p.add_argument('--port',type=int,default=8765)
    p.add_argument('--team',default='ATL')
    p.add_argument('--mode',choices=('favorite','fallback','all'),default='fallback')
    p.add_argument('--date')
    p.add_argument('--refresh',type=float,default=60)
    p.add_argument('--seconds',type=float,default=12)
    p.add_argument('--team-colors',help='JSON file of team overrides')
    p.add_argument('--scoreboard-colors',help='JSON file of global color overrides')
    args=p.parse_args()
    if args.refresh<=0 or args.seconds<=0:
        p.error('--refresh and --seconds must be positive')
    try:
        teams,scoreboard=load_palette(args.team_colors,args.scoreboard_colors)
    except (OSError,ValueError) as exc:
        p.error('invalid color configuration: '+str(exc))
    worker=BackgroundMLBFeed(MLBFeed(team=None,date=args.date,refresh_seconds=args.refresh))
    worker.start()
    started=time.monotonic()
    def frame():
        games=select_games(worker.games(),args.team,args.mode)
        if not games: return splash()
        game=games[int((time.monotonic()-started)//args.seconds)%len(games)]
        return MLBColoredScreen(game,teams,scoreboard).render()
    try:
        serve(host=args.host,port=args.port,frame_provider=frame)
    finally:
        worker.stop()
if __name__=='__main__':
    main()
