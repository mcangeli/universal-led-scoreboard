"""Rotating 64x32 MLB Classic prototype, using offline test data."""
import argparse
from .engine import ScoreboardEngine
from .screens import SplashScreen
from .mlb_classic import MLBClassicScreen
from .web_preview import serve

def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('--host',default='127.0.0.1')
    parser.add_argument('--port',type=int,default=8765)
    parser.add_argument('--seconds',type=float,default=12)
    args=parser.parse_args()
    engine=ScoreboardEngine([MLBClassicScreen(),SplashScreen()],
                            seconds_per_screen=args.seconds,splash_seconds=3)
    serve(host=args.host,port=args.port,frame_provider=engine.frame)
if __name__=='__main__':
    main()
