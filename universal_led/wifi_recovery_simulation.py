"""Exercise rollback worker behavior without invoking NetworkManager.

All scenarios use temporary state and injected command runners. This module
never starts the real worker, changes a Wi-Fi profile, or runs nmcli.
"""
from __future__ import annotations

import json
from pathlib import Path
from tempfile import TemporaryDirectory
from types import SimpleNamespace

from .wifi_recovery import recover

TOKEN='b'*32

def simulate_recovery(*, cancel=False, command_succeeds=True, corrupt=False):
    commands=[]
    with TemporaryDirectory(prefix='universal-led-recovery-test-') as directory:
        state_dir=Path(directory)
        path=state_dir/(TOKEN+'.json')
        state={'token':TOKEN,'interface':'wlan0',
               'previous_connection':'Previous WiFi','delay':0}
        if corrupt:
            state['token']='invalid'
        path.write_text(json.dumps(state),encoding='utf-8')

        def simulated_sleep(_seconds):
            if cancel:
                path.unlink(missing_ok=True)

        def simulated_run(argv,**_kwargs):
            commands.append(tuple(argv))
            return SimpleNamespace(returncode=0 if command_succeeds else 1)

        try:
            recovered=recover(TOKEN,state_dir=state_dir,
                              sleep=simulated_sleep,run=simulated_run)
            error=None
        except (ValueError,KeyError,TypeError) as exc:
            recovered=False
            error=type(exc).__name__
        return {'recovered':recovered,'cancelled':cancel,
                'command_attempted':bool(commands),
                'state_remaining':path.exists(),
                'error':error,'network_changed':False}
