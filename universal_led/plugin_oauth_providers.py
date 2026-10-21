"""Trusted provider policy for Core-managed plugin OAuth.

Only explicitly registered providers can be authorized. Plugins cannot submit
arbitrary authorization/token URLs to the configurator, preventing an OAuth
feature from becoming a credential-forwarding or SSRF endpoint.
"""
from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class Provider:
    name: str
    authorization_endpoint: str
    token_endpoint: str
    revoke_endpoint: str
    scope: str


GOOGLE_CALENDAR = Provider(
    name="google-calendar",
    authorization_endpoint="https://accounts.google.com/o/oauth2/v2/auth",
    token_endpoint="https://oauth2.googleapis.com/token",
    revoke_endpoint="https://oauth2.googleapis.com/revoke",
    scope="https://www.googleapis.com/auth/calendar.readonly",
)

# Registry entries are owned by Core, not populated from untrusted manifests.
PROVIDERS = {"google-calendar": GOOGLE_CALENDAR}
ALLOWED_PLUGINS = {"daily-calendar": frozenset({"google-calendar"})}


class ProviderError(ValueError):
    pass


def resolve_provider(plugin_id, provider_id):
    if (not isinstance(plugin_id, str) or not isinstance(provider_id, str) or
            provider_id not in ALLOWED_PLUGINS.get(plugin_id, ())):
        raise ProviderError("OAuth provider not authorized for plugin")
    return PROVIDERS[provider_id]


def public_provider_info(plugin_id, provider_id):
    provider = resolve_provider(plugin_id, provider_id)
    return {"provider": provider.name, "scope": provider.scope}
