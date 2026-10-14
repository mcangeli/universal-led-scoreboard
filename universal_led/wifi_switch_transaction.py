"""Pure Wi-Fi switch orchestration, shared by future root helper and tests.

No subprocesses, privileges or network changes occur in this module.
The caller must verify the recovery unit is armed before executing commands.
"""
from __future__ import annotations
from dataclasses import dataclass
from enum import Enum

class SwitchPhase(str, Enum):
    PREPARED = 'prepared'
    RECOVERY_ARMED = 'recovery_armed'
    SWITCH_REQUESTED = 'switch_requested'
    ASSOCIATED = 'associated'
    CONFIRMED = 'confirmed'
    RECOVERY_REQUIRED = 'recovery_required'

@dataclass(frozen=True)
class SwitchTransaction:
    previous_connection: str
    interface: str
    target_ssid: str
    phase: SwitchPhase = SwitchPhase.PREPARED
    recovery_token: str | None = None

    def transition(self, event: str, *, recovery_token: str | None = None):
        allowed = {
            (SwitchPhase.PREPARED, 'arm'): SwitchPhase.RECOVERY_ARMED,
            (SwitchPhase.RECOVERY_ARMED, 'switch'): SwitchPhase.SWITCH_REQUESTED,
            (SwitchPhase.SWITCH_REQUESTED, 'associated'): SwitchPhase.ASSOCIATED,
            (SwitchPhase.ASSOCIATED, 'confirm'): SwitchPhase.CONFIRMED,
            (SwitchPhase.RECOVERY_ARMED, 'fail'): SwitchPhase.RECOVERY_REQUIRED,
            (SwitchPhase.SWITCH_REQUESTED, 'fail'): SwitchPhase.RECOVERY_REQUIRED,
            (SwitchPhase.ASSOCIATED, 'fail'): SwitchPhase.RECOVERY_REQUIRED,
        }
        phase = allowed.get((self.phase, event))
        if phase is None:
            raise ValueError('Invalid Wi-Fi switch transition')
        token = recovery_token if event == 'arm' else self.recovery_token
        if phase == SwitchPhase.RECOVERY_ARMED and (
                not isinstance(token, str) or len(token) != 32
                or any(c not in '0123456789abcdef' for c in token)):
            raise ValueError('A valid recovery token is required before switching')
        if phase == SwitchPhase.CONFIRMED and not self.recovery_token:
            raise ValueError('Cannot confirm an unprotected switch')
        return SwitchTransaction(self.previous_connection, self.interface,
                                 self.target_ssid, phase, token)

    @property
    def may_change_network(self):
        return self.phase == SwitchPhase.RECOVERY_ARMED and bool(self.recovery_token)

    @property
    def may_cancel_recovery(self):
        return self.phase == SwitchPhase.CONFIRMED and bool(self.recovery_token)
