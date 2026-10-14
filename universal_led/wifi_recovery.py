#!/usr/bin/env python3
"""Privileged Wi-Fi recovery worker.

Run only from a root-owned systemd transient unit. This process must survive
web service restarts and never receives or logs a Wi-Fi password.
"""
from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
import subprocess
import time

STATE_DIR=Path('/run/universal-led-scoreboard/wifi-recovery')

def valid_token(token):
    return isinstance(token,str) and len(token)==32 and all(c in '0123456789abcdef' for c in token)

def recover(token, *, state_dir=STATE_DIR, sleep=time.sleep, run=subprocess.run):
    if not valid_token(token):
        raise ValueError('Invalid recovery token')
    path=state_dir/(token+'.json')
    # State files are root-owned, created with O_EXCL and mode 0600.
    with path.open(encoding='utf-8') as handle:
        data=json.load(handle)
    if data.get('token')!=token or not isinstance(data.get('previous_connection'),str) or not isinstance(data.get('interface'),str):
        raise ValueError('Invalid recovery state')
    if not data['previous_connection'] or not data['interface'].startswith('wl'):
        raise ValueError('Invalid recovery target')
    delay=max(0,min(180,int(data.get('delay',90))))
    sleep(delay)
    # Confirmation removes the state file; a missing file means no rollback.
    if not path.exists():
        return False
    # Avoid re-reading a potentially modified state file after waiting.
    result=run(['nmcli','connection','up','id',data['previous_connection'],
                'ifname',data['interface']],timeout=45,check=False,
               capture_output=True,text=True)
    if result.returncode != 0:
        # Preserve evidence of an unsuccessful rollback for diagnosis.
        return False
    path.unlink(missing_ok=True)
    return True

def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('token')
    args=parser.parse_args()
    if os.geteuid()!=0:
        parser.error('Recovery must run as root')
    recover(args.token)

if __name__=='__main__':
    main()
