# ULS Plugin Developer Guide (v0.9.0 design draft)

> **Status:** Proposed plugin contract. This guide describes the target API for the v0.9.0 Plugin Manager work. The examples are **not yet a supported, installable plugin API**. Verify implementation and tests before removing this notice.

## Choose an integration path

| Path | Best for | Integration |
| --- | --- | --- |
| Native ULS plugin | New scoreboard screens and integrations | ULS manifest, settings validation, render contract |
| Bullpen adapter | Existing MLB-LED-Scoreboard Bullpen projects | Compatibility wrapper around the original plugin |

Both paths must produce a valid 64×32 frame, work in the browser preview without matrix hardware, and respect ULS live-game interruption and rotation rules.

## Proposed native plugin package

```text
example-plugin/
  plugin.json
  example_plugin/
    __init__.py
    screen.py
  tests/
    test_screen.py
  README.md
```

Proposed manifest (field names and validation are subject to implementation):

```json
{
  "id": "example-screen",
  "name": "Example Screen",
  "version": "0.1.0",
  "api_version": "1",
  "entrypoint": "example_plugin.screen:ExampleScreen",
  "display": {"width": 64, "height": 32},
  "settings_schema": "settings.schema.json"
}
```

### Target lifecycle

1. Discover installed packages and validate manifests without importing arbitrary code.
2. Check API compatibility, dependencies, and permissions.
3. Load saved settings and validate against the plugin's schema.
4. Determine eligibility for the current rotation slot.
5. Render a frame for the 64×32 preview or physical matrix.
6. Stop cleanly, preserve settings, and report errors without crashing other screens.

The final Python class signatures must be copied from the implemented interface, not inferred from this design document.

## Adapting an existing Bullpen plugin

Bullpen plugins are not assumed to be drop-in ULS packages. A compatibility adapter should:

1. Identify the original Bullpen plugin's Python version, dependencies, configuration, and renderer interfaces.
2. Translate its configuration into a namespaced ULS settings schema, retaining unknown values during migration where safe.
3. Wrap the original renderer with a controlled 64×32 frame output and convert supported colors, fonts, and image operations.
4. Map refresh and rotation eligibility into ULS scheduling rules. Live-game precedence stays controlled by ULS.
5. Provide a fallback for unsupported Bullpen services and document any features that cannot be translated.
6. Validate import behavior and rendering without physical hardware before allowing activation.

**Do not** load arbitrary Bullpen Python modules directly inside the dashboard web process. Third-party plugin execution requires a defined trust model and appropriate isolation.

### Conversion checklist

- [ ] Original license and attribution reviewed
- [ ] Bullpen API and dependency versions recorded
- [ ] Plugin metadata and ULS compatibility declared
- [ ] 64×32 frame checked for clipping, scrolling, and color handling
- [ ] Configuration migrated without losing existing values
- [ ] No-game, offline, API failure, and restart behavior tested
- [ ] Browser preview and physical matrix behavior verified
- [ ] Disable/re-enable preserves settings
- [ ] Installation failure and rollback tested

## Plugin Manager requirements

The dashboard should distinguish **built-in modules**, **installed third-party plugins**, and **Bullpen-compatible adapters**. Each entry should show its source, version, compatibility, enabled state, and any actionable validation errors.

Disabling must preserve plugin settings. Uninstall must never silently delete user data. Installation and update should stage packages, validate manifests, reject unsafe archive paths, run compatibility checks, and roll back on failure. Do not enable executable third-party plugin installation until these protections are implemented and tested.

## Required tests before release

- Manifest parsing and invalid field rejection
- Unsupported API version rejection
- Dependency and archive traversal safeguards
- Settings preservation across disable, update, and restore
- Plugin exception isolation and frame validation
- Native plugin example renders at 64×32
- Bullpen adapter fixture renders at 64×32
- Web preview operates without a HAT
- Rotation respects live-game priority
- Existing sports and updater regression suite remains green

## Suggested example projects

Start with a simple native static/status screen to prove the API. Then use the existing Magic Number Bullpen plugin as the first real adapter integration. Green Monster and FlightWall can follow once the compatibility layer is stable.

## User-facing documentation to add after implementation

- Install a native ULS plugin from a trusted source
- Install a supported Bullpen plugin using the compatibility adapter
- Configure, enable, disable, update, and uninstall
- Diagnose missing dependencies, unsupported APIs, and render errors
- Create, test, package, and publish a plugin

This guide deliberately separates the intended contract from features already shipped. Update examples to runnable code only when the actual API and integration tests exist.
