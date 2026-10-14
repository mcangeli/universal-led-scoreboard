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

def scan_networks():
    try:
        result=subprocess.run(
            ['nmcli','--terse','--escape','yes','--fields','SSID,SIGNAL,SECURITY,IN-USE',
             'device','wifi','list','--rescan','yes'],
            capture_output=True,text=True,timeout=25,check=False)
    except (OSError,subprocess.TimeoutExpired):
        return {'available':False,'networks':[],'error':'NetworkManager scan unavailable'}
    if result.returncode:
        return {'available':False,'networks':[],'error':'Unable to scan wireless networks'}
    return {'available':True,'networks':parse_scan(result.stdout),'error':None}
