# Building native ULS plugins (API v1, ULS 0.9.0)

This is the **implemented** screen-plugin contract. Plugins are maintained separately from ULS Core. See [Swimming Fish](https://github.com/mcangeli/uls-plugins/tree/main/plugins/swimming-fish) for a working reference. Bullpen compatibility was discontinued; convert legacy Bullpen plugins to native ULS instead.

## Directory structure

```text
hello-world/
  uls-plugin.toml
  settings-schema.json
  hello_world.py
  README.md
```

The directory must have the same name as the plugin ID. ULS supports exactly **one** manifest per plugin: recommended `uls-plugin.toml`, or legacy `uls-plugin.json`. Both together are rejected. Do not use `pyproject.toml` as a ULS manifest.

### uls-plugin.toml

```toml
id = "hello-world"
name = "Hello World"
version = "0.1.0"
api_version = 1
capabilities = ["screen"]
entry_point = "hello_world:HelloWorldScreen"
description = "Minimal 64x32 example screen"
```

Fields: `id` (lowercase alphanumeric with optional separators `.`, `_`, `-`, max 100 characters); `name` (nonempty, max 120); `version` (`X.Y.Z` with optional prerelease/build suffix); `api_version` (integer 1); `capabilities` (unique nonempty array of `screen`, `provider`, `dashboard`); `entry_point` (`module:ClassName`); optional `description` (max 1000). Unknown keys are rejected. Manifest size limit is 16 KiB. **Only screen plugins have a supported execution API in 0.9.0.**

### settings-schema.json

```json
{
  "fields": {
    "display_seconds": {
      "type": "integer",
      "default": 12,
      "min": 1,
      "max": 120,
      "label": "Display duration"
    },
    "message": {
      "type": "string",
      "default": "HELLO",
      "label": "Message"
    }
  }
}
```

A screen plugin **must** declare `display_seconds` as an integer, with its schema bounds within 1–3600 seconds. At most 32 fields are supported; field names must be public Python identifiers. Supported types: `integer`, `number`, `boolean`, `string`. Each field requires a correctly typed `default`. Optional properties: numeric `min`/`max`, `choices`, `label`, `description`. Unknown fields and out-of-range values fail validation. The schema must be no larger than 16 KiB. ULS stores validated settings **outside** the plugin package, preserving them across updates.

### hello_world.py

```python
from universal_led.display import Framebuffer

class HelloWorldScreen:
    def __init__(self):
        self.message = "HELLO"

    def configure(self, settings):
        self.message = settings.get("message", "HELLO")

    def render(self):
        frame = Framebuffer(64, 32)
        frame.text(self.message[:10].upper(), 2, 12, (255, 200, 80))
        return frame
```

The entry-point class must be constructible without arguments. ULS calls `configure(settings)` if available, then `render()`. Return a `Framebuffer(64, 32)`, not PIL, PNG, PPM or raw bytes. Use `frame.pixel(x, y, (r, g, b))` and `frame.text(text, x, y, color)`. The built-in 5×7 font supports limited uppercase glyphs; unsupported characters raise errors. Keep text inside the 64×32 boundaries.

## Runtime contract and limitations

ULS launches a **new Python subprocess per requested frame**. The worker serializes the framebuffer into exactly **6144 RGB bytes** on stdout. Never print diagnostics to stdout. The default render timeout is **1.5 seconds**. No instance/module state survives across frames. There is **no supported persistent background-worker or data/cache API in 0.9.0**, and plugin dependencies are not automatically installed. Network-heavy screens should not fetch data on every render. Plugin screens are suppressed while eligible live games take priority.

Subprocess execution is **not a security sandbox**. Only install plugins from sources you trust. GitHub installs use reviewed commit hashes, and the installer validates package contents, but arbitrary Python can still be dangerous.

## Publish and install

1. Commit the plugin directory to a **public GitHub repository**. Include a README and automated tests.
2. In the ULS dashboard's **Plugin Manager**, review either a repository-root URL (`https://github.com/OWNER/REPO`) or a shared-repository plugin URL (`https://github.com/OWNER/REPO/tree/main/plugins/hello-world`).
3. Check the reviewed ID, version, source and pinned commit; install. **Installation does not automatically enable** a plugin.
4. Enable it, configure its settings, and inspect **Open Board View** during idle rotation.
5. For updates, bump the manifest version, commit, review the new GitHub commit, and update. Enabled state and external settings are preserved. **Disable before uninstalling**.

No Core catalog registration is required. Core updates and external plugin updates are separate operations.

## Validate before publishing

From a ULS checkout:

```bash
python3 - <<'PY'
from pathlib import Path
from universal_led.plugin_manifest import load_plugin_manifest
from universal_led.plugin_settings_schema import load_settings_schema
package = Path("/path/to/hello-world")
print(load_plugin_manifest(package))
print(load_settings_schema(package))
PY
```

To test the worker, put the plugin in a parent folder containing `hello-world/`:

```bash
python3 -m universal_led.native_plugin_worker \
  /absolute/path/to/parent hello-world \
  '{"display_seconds":12,"message":"HELLO"}' > /tmp/uls-hello.rgb
wc -c /tmp/uls-hello.rgb
```

Expected size: **6144 bytes**. Use the same Python environment as ULS. Add unit tests for 64×32 output, invalid settings, unsupported characters, offline behavior, and failure isolation. Test enable/disable, update, settings preservation, and browser preview on a running Pi.

## Troubleshooting

- **Manifest rejected:** both TOML and JSON present, wrong field types, wrong ID, or manifest exceeds 16 KiB.
- **GitHub review fails:** use a public repository and the supported `/tree/<branch>/plugins/<id>` directory URL.
- **Plugin does not appear:** enable it; check live-game precedence and idle rotation.
- **Worker timeout:** remove slow network requests or expensive work from `render()`.
- **Invalid schema:** declare `display_seconds` and use supported field types.
- **Frame invalid:** return exactly a 64×32 `Framebuffer`, and keep stdout free of logs.

See [installation guide](INSTALLATION.md), [0.9.0 release checklist](V090-RELEASE-CHECKLIST.md), and [external plugin examples](https://github.com/mcangeli/uls-plugins).
