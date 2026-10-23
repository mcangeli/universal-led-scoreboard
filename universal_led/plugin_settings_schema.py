"""Declarative, data-only settings schemas for native ULS plugins.

Schemas are read as JSON, never evaluated as Python. Display duration is a
reserved per-plugin setting enforced by the host scheduler.
"""
from __future__ import annotations

import json
from pathlib import Path

from .plugin_manifest import ManifestError

TYPES = {"integer", "number", "boolean", "string"}
MAX_SCHEMA_BYTES = 16384
MAX_FIELDS = 32


def validate_settings_schema(raw):
    if not isinstance(raw, dict) or set(raw) != {"fields"} or not isinstance(raw["fields"], dict):
        raise ManifestError("plugin settings schema must contain only a fields object")
    if len(raw["fields"]) > MAX_FIELDS:
        raise ManifestError("too many plugin settings")
    fields = {}
    for key, spec in raw["fields"].items():
        if (not isinstance(key, str) or not key.isidentifier()
                or key.startswith("_") or not isinstance(spec, dict)):
            raise ManifestError("invalid plugin setting name or definition")
        allowed = {"type", "default", "min", "max", "label", "description", "choices"}
        if set(spec) - allowed or spec.get("type") not in TYPES or "default" not in spec:
            raise ManifestError("invalid plugin setting definition")
        kind = spec["type"]
        default = spec["default"]
        if kind == "integer" and type(default) is not int:
            raise ManifestError("integer setting needs integer default")
        if kind == "number" and type(default) not in (int, float):
            raise ManifestError("number setting needs numeric default")
        if kind == "boolean" and type(default) is not bool:
            raise ManifestError("boolean setting needs boolean default")
        if kind == "string" and not isinstance(default, str):
            raise ManifestError("string setting needs string default")
        if kind in ("integer", "number"):
            for bound in ("min", "max"):
                if bound in spec and (type(spec[bound]) not in (int, float)
                                      or not float("-inf") < spec[bound] < float("inf")):
                    raise ManifestError("invalid numeric bound")
            if not spec.get("min", float("-inf")) <= default <= spec.get("max", float("inf")):
                raise ManifestError("default outside setting bounds")
        elif "min" in spec or "max" in spec:
            raise ManifestError("bounds only apply to numeric settings")
        for field in ("label", "description"):
            if field in spec and (not isinstance(spec[field], str) or len(spec[field]) > 300):
                raise ManifestError("invalid setting text")
        if "choices" in spec:
            choices = spec["choices"]
            if not isinstance(choices, list) or not choices or len(choices) > 30 or default not in choices:
                raise ManifestError("invalid setting choices")
        fields[key] = dict(spec)
    duration = fields.get("display_seconds")
    if duration is None or duration["type"] != "integer" or duration.get("min", 0) < 1 or duration.get("max", 3601) > 3600:
        raise ManifestError("screen plugin must declare display_seconds between 1 and 3600")
    if 'appearance_every_pages' in fields:
        raise ManifestError('appearance_every_pages is reserved for host scheduling')
    return fields


def load_settings_schema(package):
    path = Path(package) / "settings-schema.json"
    if path.is_symlink() or not path.is_file() or path.stat().st_size > MAX_SCHEMA_BYTES:
        raise ManifestError("missing or unsafe plugin settings schema")
    fields = validate_settings_schema(json.loads(path.read_text(encoding="utf-8")))
    # Host-owned control, available to every plugin without requiring plugin updates.
    fields['appearance_every_pages'] = {
        'type': 'integer', 'default': 10 if Path(package).name == 'daily-calendar' else 1,
        'min': 1, 'max': 100,
        'label': 'Show after N other pages',
        'description': 'Minimum number of regular non-live pages between appearances. Live games and alerts always take priority.',
    }
    return fields


def validated_settings(fields, values):
    if not isinstance(values, dict) or set(values) - set(fields):
        raise ManifestError("unknown plugin settings")
    result = {}
    for key, spec in fields.items():
        value = values.get(key, spec["default"])
        kind = spec["type"]
        valid = (type(value) is int if kind == "integer" else
                 type(value) in (int, float) if kind == "number" else
                 type(value) is bool if kind == "boolean" else
                 isinstance(value, str))
        if not valid:
            raise ManifestError("invalid value for " + key)
        if kind in ("integer", "number") and not spec.get("min", float("-inf")) <= value <= spec.get("max", float("inf")):
            raise ManifestError("out-of-range value for " + key)
        if "choices" in spec and value not in spec["choices"]:
            raise ManifestError("unsupported choice for " + key)
        result[key] = value
    return result
