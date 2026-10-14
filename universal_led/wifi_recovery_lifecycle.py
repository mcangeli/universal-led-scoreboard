"""Read-only systemd lifecycle inspection for an independently armed rollback.

No unit is started, stopped, cancelled or otherwise modified here.
"""
from __future__ import annotations
import re
import subprocess

UNIT_PREFIX='universal-led-wifi-recovery-'
TOKEN_RE=re.compile(r'^[0-9a-f]{32}$')

def unit_name(token):
    if not isinstance(token,str) or not TOKEN_RE.fullmatch(token):
        raise ValueError('Invalid recovery token')
    return UNIT_PREFIX+token+'.service'

def inspect_recovery_unit(token, *, run=subprocess.run):
    name=unit_name(token)
    try:
        result=run(['systemctl','--system','show',name,
                    '--property=LoadState,ActiveState,SubState,Result',
                    '--no-pager'],capture_output=True,text=True,
                   timeout=8,check=False)
    except (OSError,subprocess.TimeoutExpired):
        return {'armed':False,'unit':name,'reason':'Unable to inspect recovery unit'}
    if result.returncode:
        return {'armed':False,'unit':name,'reason':'Recovery unit not available'}
    properties={}
    for line in result.stdout.splitlines():
        if '=' in line:
            key,value=line.split('=',1)
            if key in ('LoadState','ActiveState','SubState','Result'):
                properties[key]=value
    armed=(properties.get('LoadState')=='loaded'
           and properties.get('ActiveState')=='active'
           and properties.get('SubState')=='running'
           and properties.get('Result') in ('success',''))
    return {'armed':armed,'unit':name,
            'reason':'Recovery worker running' if armed else 'Recovery worker not running'}

def require_running_recovery(token, *, run=subprocess.run):
    state=inspect_recovery_unit(token,run=run)
    if not state['armed']:
        raise RuntimeError('Independent recovery worker is not running')
    return True
