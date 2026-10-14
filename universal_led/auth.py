"""Administrator credentials and in-memory sessions for trusted LAN use.

HTTP transport is NOT encrypted. Deploy behind HTTPS before using on untrusted networks.
"""
from __future__ import annotations
import getpass
import hashlib
import hmac
import json
import os
import secrets
import threading
import time
from pathlib import Path

ITERATIONS = 600_000
SESSION_SECONDS = 8 * 3600

def set_password(directory, password):
    if len(password) < 12:
        raise ValueError('Password must contain at least 12 characters')
    path = Path(directory) / 'admin.json'
    path.parent.mkdir(parents=True, exist_ok=True)
    salt = secrets.token_bytes(32)
    value = {'version':1,'iterations':ITERATIONS,'salt':salt.hex(),
             'hash':hashlib.pbkdf2_hmac('sha256',password.encode(),salt,ITERATIONS).hex()}
    tmp = path.with_name(path.name+'.tmp-'+secrets.token_hex(6))
    try:
        with open(tmp,'x',encoding='utf-8') as stream:
            os.chmod(tmp,0o600)
            json.dump(value,stream)
        os.replace(tmp,path)
        os.chmod(path,0o600)
    finally:
        tmp.unlink(missing_ok=True)

def verify_password(directory, password):
    try:
        data=json.loads((Path(directory)/'admin.json').read_text(encoding='utf-8'))
        salt=bytes.fromhex(data['salt'])
        expected=bytes.fromhex(data['hash'])
        rounds=int(data['iterations'])
        if data['version'] != 1 or not 100_000 <= rounds <= 2_000_000:
            return False
        actual=hashlib.pbkdf2_hmac('sha256',password.encode(),salt,rounds)
        return hmac.compare_digest(actual,expected)
    except (OSError,ValueError,KeyError,TypeError):
        return False

class Sessions:
    def __init__(self):
        self._lock=threading.Lock()
        self._tokens={}
    def create(self):
        token=secrets.token_urlsafe(32)
        with self._lock:
            self._tokens[token]=time.monotonic()+SESSION_SECONDS
        return token
    def valid(self,token):
        with self._lock:
            expiry=self._tokens.get(token,0)
            if expiry <= time.monotonic():
                self._tokens.pop(token,None)
                return False
            return True
    def revoke(self,token):
        with self._lock:
            self._tokens.pop(token,None)

def configure_cli(directory):
    first=getpass.getpass('New administrator password (12+ characters): ')
    second=getpass.getpass('Confirm password: ')
    if first != second:
        raise ValueError('Passwords do not match')
    set_password(directory,first)
