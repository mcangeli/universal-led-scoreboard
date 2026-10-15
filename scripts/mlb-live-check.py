#!/usr/bin/env python3
"""Read-only live MLB readiness check. Uses same feed/parser as scoreboard."""
import argparse
from datetime import datetime
from universal_led.mlb_data import MLBFeed

def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('--date',help='YYYY-MM-DD (default: local date)')
    args=parser.parse_args()
    feed=MLBFeed(team=None,date=args.date,refresh_seconds=60)
    games=feed.games()
    if feed.last_error:
        print('MLB FEED ERROR:',feed.last_error)
        raise SystemExit(1)
    print('Schedule date:',args.date or datetime.now().astimezone().date().isoformat())
    print('Games returned:',len(games))
    for g in games:
        print(f'{g.away} @ {g.home} | {g.status.upper()} | '
              f'{g.away_runs}-{g.home_runs} | inning {g.inning} {g.inning_half} | '
              f'outs {g.outs} | bases {g.bases} | '
              f'hits {g.away_hits}-{g.home_hits} errors {g.away_errors}-{g.home_errors}')
    if not games:
        print('No games returned. Check Pi local date/time and MLB schedule.')

if __name__=='__main__':
    main()
