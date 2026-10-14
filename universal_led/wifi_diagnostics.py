"""Read-only NetworkManager diagnostics. Never expose saved Wi-Fi secrets."""
from __future__ import annotations
import subprocess

def _nmcli(*args):
    try:
        result=subprocess.run(['nmcli','--terse','--escape','no',*args],
                              capture_output=True,text=True,timeout=4,check=False)
        return result.stdout if result.returncode==0 else None
    except (OSError,subprocess.TimeoutExpired):
        return None

def wifi_status():
    """Provide a safe connectivity snapshot, without credentials or BSSIDs."""
    state=_nmcli('--fields','WIFI','general')
    device=_nmcli('--fields','DEVICE,TYPE,STATE,CONNECTION','device','status')
    if state is None or device is None:
        return {'available':False,'state':'unavailable','devices':[],
                'setup':'not enabled'}
    devices=[]
    for line in device.splitlines():
        parts=line.split(':',3)
        if len(parts)!=4 or parts[1]!='wifi':
            continue
        devices.append({'device':parts[0],'state':parts[2],
                        'connection':parts[3] if parts[2]=='connected' else ''})
    return {'available':True,'state':state.strip().splitlines()[-1] if state.strip() else 'unknown',
            'devices':devices,'setup':'not enabled'}
