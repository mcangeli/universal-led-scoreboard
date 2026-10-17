"""League-first soccer provider policy.

The native MLS/NWSL schemas are distinct from ESPN. A provider must return
normalized SoccerMatch records; raw JSON is never silently parsed as ESPN.
"""
from .soccer import SoccerMatch


class ProviderUnavailable(RuntimeError):
    """Primary source could not provide usable match data."""


class SoccerProviderRouter:
    """Prefer league feeds, with explicit ESPN fallback on failure.

    An empty valid league response is authoritative (no matches), not an
    excuse to resurrect old games from a fallback provider.
    """

    def __init__(self, league, *, primary=None, fallback=None, mode="league_first"):
        if league not in ("MLS", "NWSL"):
            raise ValueError("Unsupported league")
        if mode not in ("league_first", "league_only", "espn_only"):
            raise ValueError("Unsupported provider mode")
        self.league = league
        self.primary = primary
        self.fallback = fallback
        self.mode = mode
        self.last_source = None
        self.last_primary_error = None
        self.last_fallback_error = None

    def fetch(self, day):
        if self.mode != "espn_only":
            try:
                if self.primary is None:
                    raise ProviderUnavailable("League provider not configured")
                matches = self.primary(day)
                self._validate(matches)
                self.last_primary_error = None
                self.last_fallback_error = None
                self.last_source = "league"
                return tuple(matches)
            except (ValueError, TypeError, OSError, ProviderUnavailable) as exc:
                self.last_primary_error = str(exc)
                if self.mode == "league_only":
                    raise ProviderUnavailable(str(exc)) from exc
        if self.fallback is None:
            raise ProviderUnavailable("ESPN fallback not configured")
        try:
            matches = self.fallback(day)
            self._validate(matches)
        except (ValueError, TypeError, OSError, ProviderUnavailable) as exc:
            self.last_fallback_error = str(exc)
            self.last_source = None
            raise ProviderUnavailable(f"ESPN fallback unavailable: {exc}") from exc
        self.last_fallback_error = None
        self.last_source = "espn"
        return tuple(matches)

    def _validate(self, matches):
        if not isinstance(matches, (tuple, list)):
            raise TypeError("Provider must return a match sequence")
        if any(not isinstance(m, SoccerMatch) or m.league != self.league for m in matches):
            raise ValueError("Provider returned invalid or cross-league matches")
