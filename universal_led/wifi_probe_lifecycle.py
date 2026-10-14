"""Observe a harmless systemd probe from startup through completion.

Only the dedicated sleep-only probe is launched. This module does not import
or invoke the Wi-Fi recovery worker and never changes NetworkManager state.
"""
from __future__ import annotations

import secrets
import subprocess
import time

from .wifi_systemd_probe import run_probe

def observe_probe_lifecycle(*, run=subprocess.run, sleep=time.sleep,
                            token_factory=lambda: secrets.token_hex(8),
                            seconds=8, polls=20, interval=0.5):
    if not isinstance(polls,int) or not 1 <= polls <= 60:
        raise ValueError('Invalid poll count')
    if not isinstance(interval,(int,float)) or not 0 <= interval <= 2:
        raise ValueError('Invalid polling interval')
    started=run_probe(run=run,sleep=sleep,token_factory=token_factory,seconds=seconds)
    if not started['ok']:
        return {'ok':False,'started':False,'completed':False,
                'unit':started['unit'],'network_changed':False}
    name=started['unit']
    observed=[]
    for _ in range(polls):
        result=run(['systemctl','--system','show',name,
                    '--property=LoadState,ActiveState,SubState,Result',
                    '--no-pager'],capture_output=True,text=True,timeout=8,check=False)
        if result.returncode==0:
            fields=dict(line.split('=',1) for line in result.stdout.splitlines() if '=' in line)
            state=fields.get('ActiveState')
            substate=fields.get('SubState')
            outcome=fields.get('Result')
            observed.append(state+'/'+str(substate))
            if state=='active' and substate=='exited' and outcome=='success':
                # Stop only our dedicated sleep-only probe after observing completion.
                stopped=run(['systemctl','--system','stop',name],
                            capture_output=True,text=True,timeout=8,check=False)
                if stopped.returncode != 0:
                    break
                return {'ok':True,'started':True,'completed':True,
                        'unit':name,'observed':observed,'network_changed':False}
            if state=='failed' or outcome not in (None,'','success'):
                break
        sleep(interval)
    return {'ok':False,'started':True,'completed':False,
            'unit':name,'observed':observed,'network_changed':False}
