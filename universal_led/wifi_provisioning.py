"""Validation and safety policy for future Wi-Fi provisioning.

No network modifications are performed by this module.
"""
from __future__ import annotations

def validate_connection_request(data):
    if not isinstance(data,dict):
        raise ValueError('Expected connection settings')
    ssid=data.get('ssid')
    security=data.get('security')
    password=data.get('password','')
    if not isinstance(ssid,str) or not ssid or len(ssid.encode('utf-8'))>32 or '\x00' in ssid:
        raise ValueError('Network name must be 1 to 32 UTF-8 bytes')
    if security not in ('Open','WPA2','WPA1 WPA2','WPA2 WPA3','WPA3'):
        raise ValueError('Unsupported Wi-Fi security type')
    if not isinstance(password,str):
        raise ValueError('Invalid Wi-Fi password')
    if security=='Open':
        if password:
            raise ValueError('Open networks must not include a password')
    elif not (8<=len(password)<=63 and password.isascii()):
        raise ValueError('Wi-Fi password must contain 8 to 63 ASCII characters')
    return {'ssid':ssid,'security':security,'requires_password':security!='Open'}

def provisioning_readiness(status):
    """Prevent unsafe remote changes while connected through the same Wi-Fi."""
    devices=status.get('devices',[])
    connected=any(d.get('state')=='connected' for d in devices)
    if not status.get('available'):
        return {'ready':False,'reason':'NetworkManager unavailable'}
    if connected:
        return {'ready':False,'reason':'Active Wi-Fi must be protected by a tested rollback mechanism'}
    return {'ready':False,'reason':'Provisioning helper and rollback are not installed'}
