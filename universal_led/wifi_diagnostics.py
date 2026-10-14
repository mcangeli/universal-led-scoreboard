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

def _split_nmcli(line):
    """Parse nmcli terse rows while preserving escaped colons in names."""
    parts=[];field='';escaped=False
    for char in line:
        if escaped:
            field+=char;escaped=False
        elif char=='\\':
            escaped=True
        elif char==':':
            parts.append(field);field=''
        else:
            field+=char
    parts.append(field)
    return parts

def wifi_status():
    """Read-only connectivity and hotspot snapshot, adapted from MLB configurator."""
    state=_nmcli('--fields','WIFI','general')
    device=_nmcli('--fields','DEVICE,TYPE,STATE,CONNECTION','device','status')
    active=_nmcli('--fields','NAME,TYPE,DEVICE','connection','show','--active')
    if state is None or device is None:
        return {'available':False,'state':'unavailable','devices':[],
                'connected':False,'hotspot_active':False,'setup':'not enabled'}
    devices=[]
    for line in device.splitlines():
        parts=_split_nmcli(line)
        if len(parts)<4 or parts[1]!='wifi':
            continue
        devices.append({'device':parts[0],'state':parts[2],
                        'connection':':'.join(parts[3:]) if parts[2]=='connected' else ''})
    # NetworkManager connection TYPE '802-11-wireless' does not distinguish AP mode.
    # Query device GENERAL.TYPE and connection's 802-11-wireless.mode separately later
    # when hotspot provisioning is installed; do not infer AP mode from connection names.
    connected=any(d['state']=='connected' for d in devices)
    return {'available':True,'state':state.strip().splitlines()[-1] if state.strip() else 'unknown',
            'devices':devices,'connected':connected,'hotspot_active':None,
            'setup':'not enabled'}
