"""Pure Wi-Fi switch lifecycle state machine.

No network changes, clock reads, persistence, or privileged operations.
The caller supplies a monotonic timestamp and owns durable recovery scheduling.
"""
from __future__ import annotations

from dataclasses import dataclass, replace
from enum import Enum

from .wifi_recovery import valid_token
from .wifi_recovery_scheduler import validate_target


class SwitchPhase(str, Enum):
    PENDING = 'pending'
    CONFIRMED = 'confirmed'
    EXPIRED = 'expired'
    ROLLED_BACK = 'rolled_back'


@dataclass(frozen=True)
class WifiSwitch:
    interface: str
    previous_connection: str
    target_ssid: str
    token: str
    deadline: float
    phase: SwitchPhase = SwitchPhase.PENDING

    def __post_init__(self):
        validate_target(self.interface, self.previous_connection)
        if not isinstance(self.target_ssid, str) or not self.target_ssid:
            raise ValueError('Target SSID required')
        if not valid_token(self.token):
            raise ValueError('Invalid recovery token')
        if not isinstance(self.deadline, (int, float)) or not (0 < self.deadline < float('inf')):
            raise ValueError('Invalid deadline')

    def effective_phase(self, now):
        if self.phase is SwitchPhase.PENDING and now >= self.deadline:
            return SwitchPhase.EXPIRED
        return self.phase

    def expire(self, now):
        if self.effective_phase(now) is SwitchPhase.EXPIRED:
            return replace(self, phase=SwitchPhase.EXPIRED)
        return self

    def confirm(self, now):
        if self.effective_phase(now) is not SwitchPhase.PENDING:
            raise ValueError('Switch cannot be confirmed')
        return replace(self, phase=SwitchPhase.CONFIRMED)

    def mark_rolled_back(self):
        if self.phase not in (SwitchPhase.PENDING, SwitchPhase.EXPIRED):
            raise ValueError('Confirmed switch cannot be rolled back')
        return replace(self, phase=SwitchPhase.ROLLED_BACK)


@dataclass(frozen=True)
class SwitchRegistry:
    switches: tuple[WifiSwitch, ...] = ()

    def prepare(self, switch, now):
        if not isinstance(switch, WifiSwitch):
            raise ValueError('Invalid switch')
        if switch.phase is not SwitchPhase.PENDING or now >= switch.deadline:
            raise ValueError('Switch must have a future deadline')
        if any(existing.token == switch.token for existing in self.switches):
            raise ValueError('Duplicate recovery token')
        if any(existing.interface == switch.interface and existing.phase in
               (SwitchPhase.PENDING, SwitchPhase.EXPIRED) for existing in self.switches):
            raise ValueError('Interface already has unresolved switch')
        return SwitchRegistry(self.switches + (switch,))

    def update(self, switch):
        if not any(existing.token == switch.token for existing in self.switches):
            raise ValueError('Unknown recovery token')
        return SwitchRegistry(tuple(
            switch if existing.token == switch.token else existing
            for existing in self.switches
        ))
