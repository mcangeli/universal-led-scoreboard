"""Safely launch a temporary, non-network systemd worker for Pi validation."""
from __future__ import annotations
import secrets
import subprocess
import time

PREFIX='universal-led-systemd-probe-'
WORKER='/usr/local/libexec/universal-led-systemd-probe'

def run_probe(*, run=subprocess.run, sleep=time.sleep,
              token_factory=lambda: secrets.token_hex(8),seconds=8):
    if not isinstance(seconds,int) or not 1 <= seconds <= 20:
        raise ValueError('Invalid probe duration')
    token=token_factory()
    if not isinstance(token,str) or len(token)!=16 or any(c not in '0123456789abcdef' for c in token):
        raise ValueError('Invalid probe token')
    name=PREFIX+token+'.service'
    start=run(['systemd-run','--system','--quiet','--collect',
               '--unit='+PREFIX+token,'--property=Type=exec',
               '--property=RemainAfterExit=yes',
               WORKER,'--seconds',str(seconds)],
              capture_output=True,text=True,timeout=12,check=False)
    if start.returncode:
        raise RuntimeError('systemd rejected probe worker')
    states=[]
    for _ in range(4):
        status=run(['systemctl','--system','show',name,
                    '--property=LoadState,ActiveState,SubState','--no-pager'],
                   capture_output=True,text=True,timeout=8,check=False)
        if status.returncode==0:
            fields=dict(line.split('=',1) for line in status.stdout.splitlines() if '=' in line)
            states.append(fields.get('ActiveState','unknown')+'/'+fields.get('SubState','unknown'))
            if fields.get('LoadState')=='loaded' and fields.get('ActiveState')=='active' and fields.get('SubState')=='running':
                return {'ok':True,'unit':name,'observed':states,'network_changed':False}
        sleep(0.2)
    return {'ok':False,'unit':name,'observed':states,'network_changed':False}
