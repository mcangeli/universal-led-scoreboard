"""Administrator credentials and persistent sessions for trusted LAN use.

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
import sqlite3
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
    """Session tokens are hashed before storage; expiry and revocation persist."""
    def __init__(self, directory=None):
        self._lock=threading.Lock()
        self._tokens={} if directory is None else None
        self._directory=Path(directory) if directory is not None else None
        if self._directory is not None:
            self._directory.mkdir(parents=True,exist_ok=True)
            self._db=self._directory/'sessions.sqlite3'
            fd=os.open(self._db,os.O_CREAT|os.O_RDWR,0o600)
            os.close(fd)
            os.chmod(self._db,0o600)
            with self._connect() as conn:
                conn.execute('CREATE TABLE IF NOT EXISTS sessions (token_hash TEXT PRIMARY KEY, expires REAL NOT NULL, password_revision TEXT NOT NULL)')
                conn.execute('DELETE FROM sessions WHERE expires <= ?', (time.time(),))
    def _connect(self):
        return sqlite3.connect(self._db,timeout=5)
    def _revision(self):
        try:
            return hashlib.sha256((self._directory/'admin.json').read_bytes()).hexdigest()
        except OSError:
            return ''
    @staticmethod
    def _digest(token):
        return hashlib.sha256(token.encode('utf-8')).hexdigest()
    def create(self):
        token=secrets.token_urlsafe(32)
        with self._lock:
            if self._tokens is not None:
                self._tokens[self._digest(token)]=time.time()+SESSION_SECONDS
            else:
                with self._connect() as conn:
                    conn.execute('INSERT INTO sessions VALUES (?,?,?)',
                                 (self._digest(token),time.time()+SESSION_SECONDS,self._revision()))
        return token
    def valid(self,token):
        if not isinstance(token,str) or not 20<=len(token)<=256:
            return False
        digest=self._digest(token)
        with self._lock:
            if self._tokens is not None:
                expiry=self._tokens.get(digest,0)
                if expiry<=time.time():
                    self._tokens.pop(digest,None)
                    return False
                return True
            with self._connect() as conn:
                row=conn.execute('SELECT expires,password_revision FROM sessions WHERE token_hash=?',(digest,)).fetchone()
                if row is None:
                    return False
                if row[0]<=time.time() or not hmac.compare_digest(row[1],self._revision()):
                    conn.execute('DELETE FROM sessions WHERE token_hash=?',(digest,))
                    return False
                return True
    def revoke(self,token):
        if not isinstance(token,str):
            return
        with self._lock:
            if self._tokens is not None:
                self._tokens.pop(self._digest(token),None)
            else:
                with self._connect() as conn:
                    conn.execute('DELETE FROM sessions WHERE token_hash=?',(self._digest(token),))

def configure_cli(directory):
    first=getpass.getpass('New administrator password (12+ characters): ')
    second=getpass.getpass('Confirm password: ')
    if first != second:
        raise ValueError('Passwords do not match')
    set_password(directory,first)
