"""Wi-Fi scan and connection planning through NetworkManager.

Scanning is read-only. Applying a connection is intentionally not available
until a separate privilege-restricted helper and recovery path are installed.
"""
from __future__ import annotations
import subprocess

def parse_scan(output):
    networks={}
    for line in output.splitlines():
        # nmcli -g fields with escape=yes escapes colon and backslash.
        fields=[]; buf=''; escaped=False
        for char in line:
            if escaped:
                buf+=char; escaped=False
            elif char=='\\':
                escaped=True
            elif char==':':
                fields.append(buf);buf=''
            else:
                buf+=char
        fields.append(buf)
        if len(fields)!=4 or not fields[0].strip():
            continue
        ssid,signal,security,in_use=fields
        try:
            strength=max(0,min(100,int(signal)))
        except ValueError:
            continue
        entry={'ssid':ssid,'signal':strength,'security':security or 'Open',
               'connected':in_use.strip()=='*'}
        old=networks.get(ssid)
        if old is None or (entry['connected'],strength)>(old['connected'],old['signal']):
            networks[ssid]=entry
    return sorted(networks.values(),key=lambda n:(not n['connected'],-n['signal'],n['ssid'].lower()))


def parse_iw_scan(output):
    """Parse iw BSS blocks, including SSIDs containing colons."""
    import re
    networks=[]
    block=None
    def finish():
        if block and block.get('ssid'):
            dbm=block.get('dbm',-100)
            # Approximate percentage from received signal in dBm.
            signal=max(0,min(100,2*(dbm+100)))
            networks.append({'ssid':block['ssid'],'signal':signal,
                             'security':'WPA2' if block.get('rsn') else ('WPA1 WPA2' if block.get('wpa') else 'Open'),
                             'connected':block.get('connected',False)})
    for line in output.splitlines():
        if line.startswith('BSS '):
            finish()
            block={'connected':'-- associated' in line}
        elif block is not None:
            value=line.strip()
            if value.startswith('SSID: '):
                block['ssid']=value[6:]
            elif value.startswith('signal: '):
                match=re.search(r'-?\\d+(?:\\.\\d+)?',value[8:])
                if match: block['dbm']=float(match.group())
            elif value.startswith('RSN:'):
                block['rsn']=True
            elif value.startswith('WPA:'):
                block['wpa']=True
    finish()
    return networks

def _merge_networks(primary,secondary):
    networks={item['ssid']:item for item in primary}
    for item in secondary:
        old=networks.get(item['ssid'])
        if old is None or (item['connected'],item['signal'])>(old['connected'],old['signal']):
            networks[item['ssid']]=item
    return sorted(networks.values(),key=lambda n:(not n['connected'],-n['signal'],n['ssid'].lower()))

def _iw_scan():
    """Best-effort, unprivileged scan. Never invoke sudo from the web service."""
    try:
        device=subprocess.run(['nmcli','-g','DEVICE,TYPE','device','status'],
                              capture_output=True,text=True,timeout=4,check=False)
        if device.returncode: return []
        interfaces=[line.split(':',1)[0] for line in device.stdout.splitlines()
                    if line.endswith(':wifi') and line.split(':',1)[0].startswith('wl')]
        if not interfaces: return []
        result=subprocess.run(['iw','dev',interfaces[0],'scan'],
                              capture_output=True,text=True,timeout=12,check=False)
        return parse_iw_scan(result.stdout) if result.returncode==0 else []
    except (OSError,subprocess.TimeoutExpired):
        return []

def scan_networks():
    """Follow MLB Scoreboard Configurator: rescan interface, then list separately."""
    try:
        devices=subprocess.run(
            ['nmcli','--terse','--escape','no','--fields','DEVICE,TYPE','device','status'],
            capture_output=True,text=True,timeout=5,check=False)
        if devices.returncode:
            return {'available':False,'networks':[],'error':'Unable to identify Wi-Fi interface'}
        interfaces=[line.rsplit(':',1)[0] for line in devices.stdout.splitlines()
                    if line.endswith(':wifi')]
        if not interfaces:
            return {'available':False,'networks':[],'error':'No Wi-Fi interface found'}
        iface=interfaces[0]
        # A failed rescan must not prevent displaying cached networks.
        subprocess.run(['nmcli','device','wifi','rescan','ifname',iface],
                       capture_output=True,text=True,timeout=15,check=False)
        result=subprocess.run(
            ['nmcli','--terse','--escape','yes','--fields','SSID,SIGNAL,SECURITY,IN-USE',
             'device','wifi','list','ifname',iface],
            capture_output=True,text=True,timeout=15,check=False)
    except (OSError,subprocess.TimeoutExpired):
        return {'available':False,'networks':[],'error':'NetworkManager scan unavailable'}
    if result.returncode:
        return {'available':False,'networks':[],'error':'Unable to list wireless networks'}
    return {'available':True,'networks':parse_scan(result.stdout),'error':None}
